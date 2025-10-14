#!/usr/bin/env python3
"""
XSCRAPER Twitter-like Interface
Flask implementation matching the mockup design
"""

from flask import request, Flask, render_template, jsonify, request, send_from_directory
import lancedb
import pandas as pd
from datetime import datetime
import pytz
import os
import configparser
import json
import logging
import signal
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static', static_url_path='/static')


@app.after_request
def add_cache_control(response):
    """Add cache control headers to prevent aggressive caching"""
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response
app.config['SECRET_KEY'] = 'xscraper-twitter-2025'

# Global variables
all_items = []
user_ratings = {}
brazil_tz = pytz.timezone('America/Sao_Paulo')  # UTC-3

def load_user_ratings():
    """Load saved user ratings from JSON file"""
    global user_ratings
    ratings_file = "user_ratings.json"
    if os.path.exists(ratings_file):
        with open(ratings_file, 'r') as f:
            user_ratings = json.load(f)
    logger.info(f"Loaded {len(user_ratings)} user ratings")
    return user_ratings

def save_rating(item_id, rating):
    """Save a rating to the JSON file"""
    global user_ratings
    ratings_file = "user_ratings.json"
    
    # Load existing ratings
    if os.path.exists(ratings_file):
        with open(ratings_file, 'r') as f:
            user_ratings = json.load(f)
    
    # Add/update rating
    user_ratings[str(item_id)] = {
        'rating': float(rating), 
        'rated_at': datetime.now().isoformat()
    }
    
    # Save to file
    with open(ratings_file, 'w') as f:
        json.dump(user_ratings, f, indent=2)
    
    return True

def load_data():
    """Load data from LanceDB"""
    global all_items
    
    logger.info("Loading data from LanceDB...")
    
    # Load AWS credentials
    cred_path = os.path.expanduser("~/.aws/credentials")
    config = configparser.ConfigParser()
    config.read(cred_path)
    
    try:
        # Connect to LanceDB
        db = lancedb.connect(
            "s3://sage-unified-feed-lance/tweetss3",
            storage_options={
                "aws_access_key_id": config['default']['aws_access_key_id'],
                "aws_secret_access_key": config['default']['aws_secret_access_key'],
                "region": "us-west-2"
            }
        )
        
        # Load tweets
        logger.info("Loading tweets...")
        tweets_table = db.open_table("tweets")
        tweets = tweets_table.search().limit(2000).to_pandas()
        tweets['type'] = 'tweet'
        tweets['source'] = tweets['username']
        
        # Load news
        logger.info("Loading news...")
        news_table = db.open_table("market_news")
        news = news_table.search().limit(300).to_pandas()
        news['type'] = 'news'
        news['created_at'] = news['published_at']
        news['created_at_et'] = news['published_at_et']
        news['text'] = news['title']
        news['username'] = news['source']
        
        # Combine and sort
        cols = ['id', 'username', 'text', 'created_at', 'created_at_et', 'keywords', 'ai_enrichment', 'type']
        
        # Ensure all columns exist
        for df in [tweets, news]:
            for col in cols:
                if col not in df.columns:
                    df[col] = ''
        
        combined = pd.concat([tweets[cols], news[cols]]).sort_values('created_at', ascending=False)
        
        # Process each item
        enriched = []
        logger.info(f"Processing {len(combined)} items...")
        for idx, row in combined.iterrows():
            try:
                item = row.to_dict()
                
                # Debug logging for first few items
                if idx < 3:
                    logger.info(f"Item {idx}: created_at={item.get('created_at')}, created_at_et={item.get('created_at_et')}")
                
                # Parse keywords
                if item.get('keywords') and item['keywords'] != '':
                    try:
                        keywords = json.loads(item['keywords'])
                        if isinstance(keywords, list):
                            item['keywords_list'] = keywords[:5]
                        else:
                            item['keywords_list'] = []
                    except:
                        item['keywords_list'] = []
                else:
                    item['keywords_list'] = []
                
                # Parse AI enrichment
                if item.get('ai_enrichment'):
                    try:
                        enrichment = json.loads(item['ai_enrichment'])
                        item['ai_score'] = enrichment.get('relevance_score', 0)
                        item['category'] = enrichment.get('category', '').replace('_', ' ').title()
                        item['sentiment'] = enrichment.get('sentiment', 'neutral')
                        item['market_impact'] = enrichment.get('market_impact', '')
                    except:
                        item['ai_score'] = 0
                        item['category'] = ''
                        item['sentiment'] = 'neutral'
                        item['market_impact'] = ''
                else:
                    item['ai_score'] = 0
                    item['category'] = ''
                    item['sentiment'] = 'neutral'
                    item['market_impact'] = ''
                
                # Check user rating
                item_id = str(item['id'])
                if item_id in user_ratings:
                    item['user_rating'] = user_ratings[item_id]['rating']
                else:
                    item['user_rating'] = None
                
                # Format time - with multiple fallbacks
                time_formatted = False
                
                # Try various timestamp fields
                for time_field in ['created_at', 'created_at_et', 'fetched_at', 'published_at']:
                    if not time_formatted and time_field in item and pd.notna(item.get(time_field)):
                        try:
                            # Get the timestamp value
                            ts_value = item[time_field]
                            
                            # Parse it
                            if isinstance(ts_value, str):
                                dt = pd.to_datetime(ts_value)
                            elif hasattr(ts_value, 'to_pydatetime'):
                                dt = ts_value.to_pydatetime()
                            else:
                                dt = pd.to_datetime(ts_value)
                            
                            # Make timezone aware if needed
                            if dt.tzinfo is None:
                                dt = pytz.UTC.localize(dt)
                            
                            now = datetime.now(pytz.UTC)
                            diff = now - dt
                            
                            if diff.days > 7:
                                # Show date for old items
                                item['time_ago'] = dt.astimezone(brazil_tz).strftime('%b %d, %I:%M %p')
                            elif diff.days > 0:
                                item['time_ago'] = f"{diff.days}d"
                            elif diff.seconds > 3600:
                                hours = diff.seconds // 3600
                                item['time_ago'] = dt.astimezone(brazil_tz).strftime('%b %d, %I:%M %p')  # Full timestamp
                            elif diff.seconds > 60:
                                minutes = diff.seconds // 60
                                item['time_ago'] = dt.astimezone(brazil_tz).strftime('%b %d, %I:%M %p')  # Full timestamp
                            else:
                                item['time_ago'] = "now"
                            
                            time_formatted = True
                            logger.debug(f"Successfully formatted time from {time_field}: {item['time_ago']}")
                            
                        except Exception as e:
                            logger.debug(f"Failed to format {time_field}: {e}")
                            continue
                
                # Ultimate fallback
                if not time_formatted:
                    item['time_ago'] = datetime.now().strftime('%b %d, %I:%M %p')
                    logger.debug(f"Using fallback time for item {item.get('id', 'unknown')}")
                
                # Clean text
                item['text'] = item.get('text', '')[:500]  # Limit length
                
                enriched.append(item)
                
            except Exception as e:
                logger.error(f"Error processing item: {e}")
                continue
        
        all_items = enriched
        logger.info(f"Loaded {len(all_items)} enriched items")
        
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        all_items = []
    
    return all_items


@app.route('/api/log_error', methods=['POST'])
def log_error():
    """Log frontend errors for monitoring"""
    try:
        error_data = request.json
        logger.error(f"Frontend Error: {error_data}")
        with open('/home/ubuntu/logs/frontend_errors.log', 'a') as f:
            f.write(f"{datetime.now().isoformat()} - {error_data}\n")
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error logging frontend error: {e}")
        return jsonify({'success': False}), 500

@app.route('/')
def index():
    """Main page"""
    
    # Load and apply user ratings
    try:
        with open('user_ratings.json', 'r') as f:
            import json
            user_ratings_data = json.load(f)
            for item in all_items:
                item_id = str(item.get('id', ''))
                if item_id in user_ratings_data:
                    item['user_rating'] = user_ratings_data[item_id].get('rating')
    except Exception as e:
        print(f"Could not load user ratings: {e}")
        pass
    return render_template('twitter.html', initial_items=all_items[:50], total=len(all_items))

@app.route('/api/feed')
def get_feed():
    """Get feed data"""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    start = (page - 1) * per_page
    end = start + per_page
    
    items = all_items[start:end] if all_items else []
    
    # Load user ratings and add to items
    user_ratings = {}
    try:
        with open('user_ratings.json', 'r') as f:
            import json
            user_ratings = json.load(f)
    except:
        pass
    
    # Add user ratings to each item
    for item in items:
        item_id = item.get('id', '')
        if item_id and item_id in user_ratings:
            item['user_rating'] = user_ratings[item_id].get('rating')
    
    return jsonify({
        'items': items,
        'page': page,
        'total': len(all_items) if all_items else 0,
        'has_more': end < len(all_items) if all_items else False
    })

@app.route('/api/rate', methods=['POST'])
def rate_item():
    """Save user rating for an item"""
    try:
        # Get JSON data from request
        if not request.is_json:
            return jsonify({'success': False, 'message': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        item_id = data.get('id')
        rating = data.get('rating')
        
        if not item_id or rating is None:
            return jsonify({'success': False, 'message': 'Missing id or rating'}), 400
        
        # Validate rating
        try:
            rating = float(rating)
            if rating < 0 or rating > 10:
                return jsonify({'success': False, 'message': 'Rating must be between 0 and 10'}), 400
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid rating value'}), 400
        
        # Save to JSON file
        import json as json_lib
        import os
        ratings_file = 'user_ratings.json'
        
        # Load existing ratings
        ratings = {}
        if os.path.exists(ratings_file):
            try:
                with open(ratings_file, 'r') as f:
                    ratings = json_lib.load(f)
            except:
                ratings = {}
        
        # Update rating
        ratings[str(item_id)] = {
            'rating': rating,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save back to file
        with open(ratings_file, 'w') as f:
            json_lib.dump(ratings, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': f'Rating saved successfully',
            'rating': rating,
            'id': item_id
        })
        
    except Exception as e:
        print(f'Error in rate_item: {str(e)}')
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/refresh')
def refresh_data():
    """Refresh data from database"""
    load_data()
    load_user_ratings()
    return jsonify({'success': True, 'items': len(all_items)})

@app.route('/api/debug')
def debug_data():
    """Debug endpoint to check data"""
    sample_items = all_items[:3] if all_items else []
    debug_info = {
        'total_items': len(all_items),
        'sample_items': []
    }
    
    for item in sample_items:
        debug_info['sample_items'].append({
            'id': item.get('id', 'N/A'),
            'username': item.get('username', 'N/A'),
            'time_ago': item.get('time_ago', 'N/A'),
            'created_at': str(item.get('created_at', 'N/A')),
            'created_at_et': str(item.get('created_at_et', 'N/A')),
            'type': item.get('type', 'N/A')
        })
    
    return jsonify(debug_info)

def signal_handler(sig, frame):
    """Handle shutdown gracefully"""
    logger.info('Shutting down gracefully...')
    sys.exit(0)

if __name__ == '__main__':
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Load data on startup
    load_user_ratings()
    load_data()
    
    # Run the app
    logger.info("Starting XSCRAPER Twitter interface on port 8509...")
    app.run(
        host='0.0.0.0',
        port=8509,
        debug=False
    )
