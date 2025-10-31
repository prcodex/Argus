#!/usr/bin/env python3
"""
SAGE 4.0 - Single Database Interface (FIXED)
Flask application serving the unified feed from single LanceDB with custom_fields
"""

import os
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import lancedb
import pandas as pd
import numpy as np
import re

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)
app.config['JSON_SORT_KEYS'] = False

# Add cache control headers to all responses
@app.after_request
def add_cache_headers(response):
    """Add cache control headers to prevent browser caching"""
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        if value == '' or value.lower() == 'none':
            return default
        try:
            return float(value)
        except ValueError:
            return default
    return default


class SAGE4Interface:
    """SAGE 4.0 Interface - Single LanceDB with infinite flexibility"""
    
    # Define sender detection rules (domain -> sender tag)
    SENDER_RULES = {
        '@gs.com': 'Goldman Sachs',
        '@goldmansachs.com': 'Goldman Sachs',
        '@itau.com.br': 'Itau',
        '@itau.com': 'Itau',
        '@itaubba.com.br': 'Itau',
        '@bloomberg.com': 'Bloomberg',
        '@bloomberg.net': 'Bloomberg',
        '@ft.com': 'Financial Times',
        '@wsj.com': 'Wall Street Journal',
        '@dowjones.com': 'Wall Street Journal',
        '@jpmorgan.com': 'J.P. Morgan',
        '@jpmchase.com': 'J.P. Morgan',
        '@rosenbergresearch.com': 'Rosenberg Research',
        '@substack.com': 'Substack Newsletters',
        '@morganstanley.com': 'Morgan Stanley',
        '@citi.com': 'Citigroup',
        '@citigroup.com': 'Citigroup',
        '@bankofamerica.com': 'Bank of America',
        '@barclays.com': 'Barclays',
        '@db.com': 'Deutsche Bank',
        '@deutschebank.com': 'Deutsche Bank'
    }
    
    def safe_float(self, value, default=None):
        """Safely convert a value to float"""
        if value is None or pd.isna(value):
            return default
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            if value == '' or value.lower() == 'none':
                return default
            try:
                return float(value)
            except ValueError:
                return default
        return default

    def __init__(self):
        """Initialize SAGE 4.0 connection"""
        try:
            # Connect to SAGE 4.0 database
            self.db = lancedb.connect("s3://sage-unified-feed-lance/sage4/")
            self.table = self.db.open_table("unified_feed")
            logger.info("✅ Connected to SAGE 4.0 single database")
        except Exception as e:
            logger.error(f"Failed to connect to SAGE 4.0: {e}")
            raise
    
    def get_feed(self, filter_tag=None, limit=100, offset=0):
        """Get feed items with filtering"""
        try:
            # ALWAYS refresh table connection to get latest data from S3
            self.table = self.db.open_table("unified_feed")
            
            # Get all data
            df = self.table.to_pandas()
            
            # Filter by tag if specified
            if filter_tag and filter_tag != 'all':
                if filter_tag == 'email':
                    df = df[df['source_type'] == 'email']
                elif filter_tag == 'twitter':
                    df = df[df['source_type'] == 'twitter']
                elif filter_tag == 'newsfeed':
                    # Filter by Feed_Type_Flag = 'newsfeed'
                    mask = df.apply(
                        lambda row: row.get('custom_fields', {}).get('Feed_Type_Flag') == 'newsfeed' 
                        if isinstance(row.get('custom_fields'), dict) else False,
                        axis=1
                    )
                    df = df[mask]
                    logger.info(f"Found {mask.sum()} items with Feed_Type_Flag='newsfeed'")
                elif filter_tag == 'goldman_sachs':
                    # Check for Goldman Sachs with enhanced email detection
                    mask = df.apply(
                        lambda row: self._check_goldman_sachs(
                            row.get('custom_fields', {}) if isinstance(row.get('custom_fields'), dict) else {},
                            row
                        ),
                        axis=1
                    )
                    df = df[mask]
                elif filter_tag.startswith('sender:'):
                    # Handle sender-specific filters
                    sender_name = filter_tag.replace('sender:', '').strip()
                    logger.info(f"Filtering by sender: {sender_name}")
                    
                    # First check stored SenderTag, then fall back to dynamic detection
                    def check_sender(row):
                        # Check stored SenderTag first (faster)
                        custom_fields = row.get('custom_fields', {})
                        if isinstance(custom_fields, dict):
                            if custom_fields.get('SenderTag') == sender_name:
                                return True
                        
                        # Fall back to dynamic detection
                        return self.detect_sender_from_email(row) == sender_name
                    
                    mask = df.apply(check_sender, axis=1)
                    df = df[mask]
                    logger.info(f"Found {mask.sum()} items for sender: {sender_name} (using stored tags + dynamic detection)")
            
            # Sort by created_at
            df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
            df = df.sort_values('created_at', ascending=False, na_position='last')
            
            # Apply pagination
            total_count = len(df)
            df_page = df.iloc[offset:offset + limit]
            
            # Convert to records
            items = []
            for _, row in df_page.iterrows():
                item = self._format_item(row)
                items.append(item)
            
            return {
                'items': items,
                'total': total_count,
                'has_more': (offset + limit) < total_count
            }
            
        except Exception as e:
            logger.error(f"Error getting feed: {e}")
            import traceback
            traceback.print_exc()
            return {'items': [], 'total': 0, 'has_more': False}
    
    def _check_goldman_sachs(self, custom_fields, row_data=None):
        """Check if item is from Goldman Sachs - Enhanced with email domain detection"""
        # Method 1: Check email domain for @gs.com
        if row_data is not None:
            # Check author_email field
            author_email = row_data.get('author_email', '')
            if author_email and '@gs.com' in str(author_email).lower():
                logger.info(f"Detected Goldman Sachs by email: {author_email}")
                return True
            
            # Check author field for email patterns
            author = row_data.get('author', '')
            if author and '@gs.com' in str(author).lower():
                logger.info(f"Detected Goldman Sachs in author field: {author}")
                return True
            
            # Check content_text for From: lines with @gs.com
            content = row_data.get('content_text', '')
            if content:
                import re
                # Look for email patterns in content
                from_pattern = r'From:.*@gs\.com'
                sender_pattern = r'Sender:.*@gs\.com'
                reply_to_pattern = r'Reply-To:.*@gs\.com'
                
                if (re.search(from_pattern, content, re.IGNORECASE) or 
                    re.search(sender_pattern, content, re.IGNORECASE) or
                    re.search(reply_to_pattern, content, re.IGNORECASE)):
                    logger.info("Detected Goldman Sachs by email header in content")
                    return True
        
        if not custom_fields:
            return False
        
        # Method 2: Check sender in custom_fields
        sender = custom_fields.get('sender', {})
        if sender:
            # Check sender email
            sender_email = sender.get('email', '')
            if sender_email and '@gs.com' in str(sender_email).lower():
                logger.info(f"Detected Goldman Sachs by sender email in custom_fields: {sender_email}")
                return True
            # Check sender tag
            if sender.get('tag', '').lower() == 'goldman sachs':
                return True
        
        # Method 3: Check tags (existing)
        tags = custom_fields.get('tags', {})
        if tags:
            custom_tags = tags.get('custom_tags', [])
            if isinstance(custom_tags, list):
                for tag in custom_tags:
                    if 'goldman' in str(tag).lower():
                        return True
        
        return False
    
    def _format_item(self, row):
        """Format item for API response"""
        try:
            # Get custom fields safely
            custom_fields = row.get('custom_fields', {})
            if not isinstance(custom_fields, dict):
                custom_fields = {}
            
            # Format created_at
            created_at = row.get('created_at')
            if pd.notna(created_at):
                if hasattr(created_at, 'isoformat'):
                    created_at_str = created_at.isoformat()
                else:
                    created_at_str = str(created_at)
            else:
                created_at_str = datetime.now().isoformat()
            
            # Build response
            # Get sender_tag from custom_fields if available
            sender_tag = None
            if isinstance(custom_fields, dict):
                sender_tag = custom_fields.get('SenderTag', '')
                if sender_tag and sender_tag.strip():
                    sender_tag = sender_tag.strip()
                else:
                    sender_tag = None
            
            # Use sender_tag if available, otherwise fall back to author
            display_author = sender_tag if sender_tag else row.get('author', '')
            
            item = {
                'id': str(row.get('id', '')),
                'source_type': row.get('source_type', 'unknown'),
                'created_at': created_at_str,
                'author': display_author,  # Now shows sender_tag instead of "Pedro Ribeiro"
                'original_author': row.get('author', ''),  # Keep original for reference
                'sender_tag': sender_tag,  # Pass sender_tag separately
                'title': row.get('title', row.get('subject', '')),
                'content_html': row.get('content_html', ''),
                'content_text': row.get('content_text', '')[:500] if row.get('content_text') else '',
                
                # Add AI fields - handle NaN values and get correct column names
                'ai_score': None if pd.isna(row.get('ai_relevance_score')) else self.safe_float(row.get('ai_relevance_score'), None) if row.get('ai_relevance_score') is not None else None,
                'ai_sentiment': '' if pd.isna(row.get('ai_sentiment')) else str(row.get('ai_sentiment', '')),
                                'ai_summary': '' if pd.isna(row.get('ai_summary')) else str(row.get('ai_summary', '')),
                'ai_keywords': '' if pd.isna(row.get('ai_keywords')) else str(row.get('ai_keywords', '')),
                'ai_category': '' if pd.isna(row.get('ai_category')) else str(row.get('ai_category', '')),
                'ai_market_impact': '' if pd.isna(row.get('ai_market_impact')) else str(row.get('ai_market_impact', '')),
                'ai_reasoning': '' if pd.isna(row.get('ai_reasoning')) else str(row.get('ai_reasoning', '')),
                'user_rating': None if pd.isna(row.get('user_rating')) else float(row.get('user_rating')) if row.get('user_rating') is not None else None,
                
                # Add filter tags for compatibility with SAGE 3.0 interface
                'filter_tags': self._get_filter_tags(row, custom_fields)
            }
            
            # Debug logging for AI fields (first 3 items)
            import random
            if random.random() < 0.1:  # Log 10% of items
                logger.info(f"DEBUG: Item {row.get('id', 'unknown')[:8]}...")
                logger.info(f"  - ai_relevance_score in DB: {row.get('ai_relevance_score', 'NOT FOUND')}")
                logger.info(f"  - ai_sentiment in DB: {row.get('ai_sentiment', 'NOT FOUND')}")
                logger.info(f"  - ai_summary in DB: {row.get('ai_summary', 'NOT FOUND')[:50] if row.get('ai_summary') else 'NOT FOUND'}")
                logger.info(f"  - Sending ai_score as: {item['ai_score']}")
            
            # Debug logging for problematic email
            if str(row.get('id', '')) == '7974836d5de6353d081863649065e2e8':
                logger.info(f"DEBUG: Formatting email 797483...")
                logger.info(f"  - DB title: {row.get('title', 'N/A')}")
                logger.info(f"  - DB subject: {row.get('subject', 'N/A')}")
                logger.info(f"  - DB content_text first 50: {str(row.get('content_text', ''))[:50]}")
                logger.info(f"  - API title being sent: {item['title']}")
                logger.info(f"  - API content_text being sent first 50: {item['content_text'][:50]}")
            
            return item
            
        except Exception as e:
            logger.error(f"Error formatting item: {e}")
            return {
                'id': 'error',
                'source_type': 'error',
                'created_at': datetime.now().isoformat(),
                'author': 'Error',
                'title': 'Error loading item',
                'content_html': '',
                'content_text': str(e),
                'filter_tags': []
            }
    
    def determine_feed_type_flag(self, row_data):
        """Determine Feed_Type_Flag for an item"""
        # Check source_type first
        source_type = row_data.get('source_type', '')
        if source_type == 'twitter':
            return 'newsfeed'
        
        # Check SenderTag - ONLY Bloomberg Feed (alerts), NOT Bloomberg News (editorial)
        custom_fields = row_data.get('custom_fields', {})
        if isinstance(custom_fields, dict):
            sender_tag = custom_fields.get('SenderTag', '')
            if sender_tag == 'Bloomberg Feed':  # Alerts/feeds only
                return 'newsfeed'
        
        # Everything else is "other" (including Bloomberg News)
        return 'other'
    
    def detect_sender_from_email(self, row_data):
        """Detect sender organization from email patterns"""
        # Check author field for specific patterns first
        author = str(row_data.get('author', '')).lower()
        title = str(row_data.get('title', '')).lower()
        
        # PRIORITY 1: Check Itau BEFORE Bloomberg (to prevent mis-tagging)
        if 'itau' in author or 'itaú' in author or 'itaù' in author:
            logger.info(f"Detected Itau from author: {row_data.get('author')}")
            return 'Itau'
        if 'itau' in title or 'itaú' in title or 'ita ' in title:
            logger.info(f"Detected Itau from title: {row_data.get('title')}")
            return 'Itau'
        
        # PRIORITY 2: Check Substack (independent media)
        if 'substack' in author:
            logger.info(f"Detected Substack from author: {row_data.get('author')}")
            return 'Substack Newsletters'
        if 'substack' in title:
            logger.info(f"Detected Substack from title: {row_data.get('title')}")
            return 'Substack Newsletters'
        # Check content for substack.com
        content_text = str(row_data.get('content_text', '') or '')[:2000].lower()
        content_html = str(row_data.get('content_html', '') or '')[:2000].lower()
        if 'substack.com' in content_text or 'substack.com' in content_html:
            logger.info(f"Detected Substack from content")
            return 'Substack Newsletters'
        
        # PRIORITY 3: Other direct author pattern matching
        if 'gs macro' in author or 'goldman sachs' in author or 'gs research' in author:
            logger.info(f"Detected Goldman Sachs from author: {row_data.get('author')}")
            return 'Goldman Sachs'
        if 'bloomberg' in author:
            return 'Bloomberg'
        if 'wsj' in author or 'wall street journal' in author:
            return 'Wall Street Journal'
        if 'rosenberg' in author:
            return 'Rosenberg Research'
        if 'ft.com' in author or 'financial times' in author:
            return 'Financial Times'
        if 'jpmorgan' in author or 'j.p. morgan' in author or 'jp morgan' in author:
            return 'J.P. Morgan'
        
        # Check various fields for email addresses
        fields_to_check = ['author_email', 'author', 'content_text']
        
        for field in fields_to_check:
            value = row_data.get(field, '')
            if value:
                value_str = str(value).lower()
                # Check each sender rule
                for domain, sender_tag in self.SENDER_RULES.items():
                    if domain in value_str:
                        logger.info(f"Detected {sender_tag} from {domain} in {field}")
                        return sender_tag
        
        # Check custom_fields
        custom_fields = row_data.get('custom_fields', {})
        if isinstance(custom_fields, dict):
            sender = custom_fields.get('sender', {})
            if sender and isinstance(sender, dict):
                sender_email = sender.get('email', '')
                if sender_email:
                    email_lower = str(sender_email).lower()
                    for domain, sender_tag in self.SENDER_RULES.items():
                        if domain in email_lower:
                            logger.info(f"Detected {sender_tag} from {domain} in custom_fields")
                            return sender_tag
        
        return None
    
    def _get_filter_tags(self, row, custom_fields):
        """Get filter tags for an item"""
        tags = []
        
        # Add source type as tag
        source_type = row.get('source_type', '')
        if source_type:
            tags.append(source_type)
        
        # Check for Goldman Sachs with full row data
        if self._check_goldman_sachs(custom_fields, row):
            tags.append('goldman_sachs')
        
        return tags
    
    def get_email(self, email_id):
        """Get a single email by ID"""
        try:
            # Get fresh data from database
            df = self.table.to_pandas()
            logger.info(f"Looking for email ID: {email_id}")
            logger.info(f"Total records in database: {len(df)}")
            
            # Find the email by ID
            mask = df['id'] == email_id
            logger.info(f"Matching records found: {mask.sum()}")
            
            if not mask.any():
                # Debug: show some sample IDs
                sample_ids = df['id'].head(3).tolist()
                logger.warning(f"Email {email_id} not found. Sample IDs: {sample_ids}")
                return None
            
            row = df[mask].iloc[0]
            
            # Get custom fields
            custom_fields = row.get('custom_fields', {})
            if pd.isna(custom_fields) or custom_fields is None:
                custom_fields = {}
            elif not isinstance(custom_fields, dict):
                custom_fields = {}
            
            # Format created_at with proper timezone handling
            import pytz
            created_at = row.get('created_at')
            if pd.notna(created_at):
                # Parse timestamp - stored as UTC
                ts = pd.to_datetime(created_at)
                if ts.tzinfo is None:
                    # Assume UTC if no timezone
                    utc_tz = pytz.UTC
                    ts = utc_tz.localize(ts)
                # Convert to ET
                et_tz = pytz.timezone('America/New_York')
                ts_et = ts.astimezone(et_tz)
                # Return as ISO string with ET timezone offset
                created_at_str = ts_et.isoformat()
            else:
                created_at_str = datetime.now().isoformat()
            
            # Build full email response
            # Get author_email safely
            author_email = row.get('author_email', '')
            if not author_email and custom_fields:
                sender = custom_fields.get('sender', {})
                if isinstance(sender, dict):
                    author_email = sender.get('email', '')
            
            email_data = {
                'id': str(row.get('id', '')),
                'source_type': row.get('source_type', 'email'),
                'created_at': created_at_str,
                'author': row.get('author', ''),
                'author_email': author_email,
                'title': row.get('title', row.get('subject', '')),
                'subject': row.get('title', row.get('subject', '')),
                'content_html': row.get('content_html', ''),
                'content_text': row.get('content_text', ''),
                'is_goldman': self._check_goldman_sachs(custom_fields, row),
                'filter_tags': self._get_filter_tags(row, custom_fields)
            }
            
            return email_data
            
        except Exception as e:
            logger.error(f"Error getting email {email_id}: {e}")
            import traceback
            traceback.print_exc()
            return None

# Initialize SAGE 4.0 interface
sage4 = SAGE4Interface()

@app.route('/')
def index():
    """Main interface"""
    return render_template('sage_4.0_interface.html')

@app.route('/test_display.html')
def test_display():
    """Test display page for debugging"""
    with open('test_display.html', 'r') as f:
        return f.read()

@app.route('/debug_display.html')
def debug_display():
    """Debug display page"""
    with open('debug_display.html', 'r') as f:
        return f.read()

@app.route('/test_api.html')
def test_api():
    """Test API page"""
    with open('test_api.html', 'r') as f:
        return f.read()

@app.route('/debug_inline.html')
def debug_inline():
    """Debug inline display page"""
    with open('debug_inline.html', 'r') as f:
        return f.read()

@app.route('/test_email_detail.html')
def test_email_detail():
    """Test email detail display page"""
    with open('test_email_detail.html', 'r') as f:
        return f.read()

@app.route('/api/feed')
def api_feed():
    """Get feed items - Compatible with SAGE 3.0 interface"""
    import pytz
    import pandas as pd
    
    # Accept both 'filter' and 'type' for compatibility
    filter_tag = request.args.get('type') or request.args.get('filter', 'all')
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))
    
    result = sage4.get_feed(
        filter_tag=filter_tag,
        limit=limit,
        offset=offset
    )
    
    # Fix timezone - timestamps are stored as UTC, convert to ET
    et_tz = pytz.timezone('America/New_York')
    utc_tz = pytz.UTC
    for item in result.get('items', []):
        if 'created_at' in item and item['created_at']:
            # Parse timestamp - stored as UTC
            ts = pd.to_datetime(item['created_at'])
            if ts.tzinfo is None:
                # Assume UTC if no timezone
                ts = utc_tz.localize(ts)
            # Convert to ET
            ts_et = ts.astimezone(et_tz)
            # Return as ISO string with ET timezone offset
            item['created_at'] = ts_et.isoformat()
    
    return jsonify(result)


@app.route('/config')
def config_page():
    """Sender configuration page"""
    return render_template('sage_config.html')

@app.route('/api/feed-type-stats')
def feed_type_stats():
    """Get Feed_Type_Flag statistics"""
    try:
        # Get all data
        df = sage4.table.to_pandas()
        
        # Count by Feed_Type_Flag
        type_counts = {'newsfeed': 0, 'other': 0}
        
        for _, row in df.iterrows():
            custom_fields = row.get('custom_fields', {})
            if isinstance(custom_fields, dict):
                feed_type = custom_fields.get('Feed_Type_Flag', 'other')
                type_counts[feed_type] = type_counts.get(feed_type, 0) + 1
        
        return jsonify(type_counts)
        
    except Exception as e:
        logger.error(f"Error getting feed type stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sender-stats')
def sender_stats():
    """Get sender statistics with enhanced email detection"""
    try:
        # Get all data
        df = sage4.table.to_pandas()
        
        # Count by sender using enhanced detection
        sender_counts = {}
        detected_senders = []
        
        for _, row in df.iterrows():
            # First check stored SenderTag (priority)
            custom_fields = row.get('custom_fields', {})
            sender_tag = None
            
            if isinstance(custom_fields, dict):
                sender_tag = custom_fields.get('SenderTag')
            
            if sender_tag:
                # Use stored SenderTag
                sender_counts[sender_tag] = sender_counts.get(sender_tag, 0) + 1
                if sender_tag not in detected_senders:
                    detected_senders.append(sender_tag)
            else:
                # Fall back to dynamic detection for untagged items
                detected_sender = sage4.detect_sender_from_email(row)
                
                if detected_sender:
                    sender_counts[detected_sender] = sender_counts.get(detected_sender, 0) + 1
                    if detected_sender not in detected_senders:
                        detected_senders.append(detected_sender)
        
        # Log detection results
        if detected_senders:
            logger.info(f"Detected senders by email domain: {detected_senders}")
        
        return jsonify(sender_counts)
    except Exception as e:
        logger.error(f"Error getting sender stats: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({})

@app.route('/api/email/<email_id>')
def api_email(email_id):
    """Get single email details"""
    try:
        # Decode the email ID (it might be URL encoded)
        from urllib.parse import unquote
        email_id = unquote(email_id)
        
        email_data = sage4.get_email(email_id)
        if email_data:
            return jsonify(email_data)
        else:
            return jsonify({'error': 'Email not found'}), 404
    except Exception as e:
        logger.error(f"Error in api_email: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/manual-fetch', methods=['POST'])
def manual_fetch():
    """Manually trigger a Gmail fetch"""
    import subprocess
    import os
    try:
        # Setup environment with Gmail credentials
        env = os.environ.copy()
        
        # Load Gmail credentials from file
        gmail_env_file = '/home/ubuntu/newspaper_project/gmail_env.sh'
        if os.path.exists(gmail_env_file):
            with open(gmail_env_file, 'r') as f:
                for line in f:
                    if line.startswith('export '):
                        line = line.replace('export ', '').strip()
                        if '=' in line:
                            key, value = line.split('=', 1)
                            # Remove quotes if present
                            value = value.strip('"').strip("'")
                            env[key] = value
        
        # Run the ROBUST Gmail fetcher for manual fetch (fast and reliable)
        result = subprocess.run(
            ['/usr/bin/python3', '/home/ubuntu/newspaper_project/sage4_gmail_robust.py'],
            capture_output=True,
            text=True,
            timeout=120,  # 2 minute timeout for robust fetch
            env=env
        )
        
        # Parse output for statistics
        output_lines = result.stdout.split('\n')
        stats = {
            'success': result.returncode == 0,
            'new_emails': 0,
            'processed': 0,
            'blocked': 0,
            'message': ''
        }
        
        for line in output_lines:
            if 'NEW EMAILS ADDED:' in line:
                try:
                    stats['new_emails'] = int(line.split(':')[1].strip())
                except:
                    pass
            elif 'Processed:' in line:
                try:
                    stats['processed'] = int(line.split(':')[1].strip().split()[0])
                except:
                    pass
            elif 'Blocked (spam):' in line:
                try:
                    stats['blocked'] = int(line.split(':')[1].strip())
                except:
                    pass
        
        if result.returncode == 0:
            if stats['new_emails'] > 0:
                stats['message'] = f"Fetched {stats['new_emails']} new emails! (Processed {stats['processed']} total)"
            else:
                stats['message'] = f"No new emails found (Checked {stats['processed']} emails)"
        else:
            stats['message'] = "Fetch completed with warnings"
        
        logger.info(f"Manual fetch completed: {stats}")
        return jsonify(stats)
        
    except subprocess.TimeoutExpired:
        logger.error("Manual fetch timed out")
        return jsonify({
            'success': False,
            'message': 'Fetch timed out after 5 minutes (still processing in background)'
        }), 408
    except Exception as e:
        logger.error(f"Error in manual fetch: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        df = sage4.table.to_pandas()
        return jsonify({
            'status': 'healthy',
            'version': '4.0',
            'architecture': 'single_database',
            'total_items': len(df),
            'custom_fields': 'enabled',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/set_user_rating', methods=['POST'])
def set_user_rating():
    """Set user rating for an item"""
    try:
        data = request.json
        item_id = data.get('item_id')
        rating = data.get('rating')
        
        logger.info(f"Setting user rating for {item_id}: {rating}")
        
        # Update in LanceDB
        import lancedb
        import pandas as pd
        
        db = lancedb.connect("s3://sage-unified-feed-lance/sage4/")
        table = db.open_table("unified_feed")
        df = table.to_pandas()
        
        # Update the rating
        df.loc[df['id'] == item_id, 'user_rating'] = rating
        
        # Save back to LanceDB
        db.drop_table("unified_feed")
        table = db.create_table("unified_feed", df)
        
        return jsonify({'success': True, 'message': 'Rating saved'})
        
    except Exception as e:
        logger.error(f"Error setting user rating: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500




# ========== Sender Blocking API Endpoints ==========

@app.route('/api/block-sender', methods=['POST'])
def block_sender():
    """Add a sender pattern to the block list"""
    try:
        data = request.json
        pattern = data.get('pattern')
        pattern_type = data.get('pattern_type', 'exact')
        reason = data.get('reason', '')
        
        if not pattern:
            return jsonify({'success': False, 'error': 'Pattern is required'})
        
        # Connect to LanceDB
        s3_path = "s3://sage-unified-feed-lance/sage4/"
        db = lancedb.connect(s3_path)
        
        # Get existing blocked senders
        try:
            blocked_table = db.open_table("blocked_senders")
            blocked_df = blocked_table.to_pandas()
        except:
            # Table doesn't exist, create it
            blocked_df = pd.DataFrame(columns=['pattern', 'pattern_type', 'added_date', 'added_by', 'reason', 'emails_blocked'])
        
        # Check if pattern already exists
        if not blocked_df.empty and pattern in blocked_df['pattern'].values:
            return jsonify({'success': False, 'error': 'Pattern already blocked'})
        
        # Add new pattern
        new_block = pd.DataFrame([{
            'pattern': pattern,
            'pattern_type': pattern_type,
            'added_date': datetime.now().isoformat(),
            'added_by': 'user',
            'reason': reason,
            'emails_blocked': 0
        }])
        
        blocked_df = pd.concat([blocked_df, new_block], ignore_index=True)
        
        # Update table
        db.create_table("blocked_senders", blocked_df, mode="overwrite")
        
        logger.info(f"Blocked sender pattern: {pattern} ({pattern_type})")
        return jsonify({'success': True, 'message': f'Blocked {pattern}'})
        
    except Exception as e:
        logger.error(f"Error blocking sender: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/blocked-senders', methods=['GET'])
def get_blocked_senders():
    """Get list of blocked sender patterns"""
    try:
        # Connect to LanceDB
        s3_path = "s3://sage-unified-feed-lance/sage4/"
        db = lancedb.connect(s3_path)
        
        # Get blocked senders
        try:
            blocked_table = db.open_table("blocked_senders")
            blocked_df = blocked_table.to_pandas()
            
            # Convert to list of dicts
            blocked_list = blocked_df.to_dict('records')
            
            # Calculate total blocked emails
            total_blocked = int(blocked_df['emails_blocked'].sum()) if not blocked_df.empty else 0
        except:
            # Table doesn't exist
            blocked_list = []
            total_blocked = 0
        
        return jsonify({
            'blocked_senders': blocked_list,
            'total_blocked': total_blocked
        })
        
    except Exception as e:
        logger.error(f"Error getting blocked senders: {str(e)}")
        return jsonify({'blocked_senders': [], 'total_blocked': 0, 'error': str(e)})

@app.route('/api/unblock-sender', methods=['POST'])
def unblock_sender():
    """Remove a sender pattern from the block list"""
    try:
        data = request.json
        pattern = data.get('pattern')
        
        if not pattern:
            return jsonify({'success': False, 'error': 'Pattern is required'})
        
        # Connect to LanceDB
        s3_path = "s3://sage-unified-feed-lance/sage4/"
        db = lancedb.connect(s3_path)
        
        # Get blocked senders
        try:
            blocked_table = db.open_table("blocked_senders")
            blocked_df = blocked_table.to_pandas()
            
            # Remove the pattern
            original_count = len(blocked_df)
            blocked_df = blocked_df[blocked_df['pattern'] != pattern]
            
            if len(blocked_df) == original_count:
                return jsonify({'success': False, 'error': 'Pattern not found'})
            
            # Update table
            if blocked_df.empty:
                # If no patterns left, still keep the table with empty dataframe
                empty_df = pd.DataFrame(columns=['pattern', 'pattern_type', 'added_date', 'added_by', 'reason', 'emails_blocked'])
                db.create_table("blocked_senders", empty_df, mode="overwrite")
            else:
                db.create_table("blocked_senders", blocked_df, mode="overwrite")
            
            logger.info(f"Unblocked sender pattern: {pattern}")
            return jsonify({'success': True, 'message': f'Unblocked {pattern}'})
            
        except:
            return jsonify({'success': False, 'error': 'Block list not found'})
        
    except Exception as e:
        logger.error(f"Error unblocking sender: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8540))
    logger.info(f"Starting SAGE 4.0 on port {port}")
    logger.info("Single database architecture with infinite flexibility via custom_fields")
    app.run(host='0.0.0.0', port=port, debug=False)  # debug=False for stability
