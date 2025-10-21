# SAGE AI Source Code

This directory contains the core SAGE AI system files.

## Main Components

### sage4_interface_fixed.py
The main Flask application serving the SAGE AI interface on port 8540.

**Key Features:**
- LanceDB integration for data storage on S3
- AI enrichment with Claude API
- Sender detection and categorization
- User rating system
- Beautiful HTML email display
- Auto-refresh functionality

### comprehensive_sender_update.py
Comprehensive sender detection and categorization system.

**Features:**
- Pattern-based sender detection
- Email domain parsing
- Subject line analysis
- Bulk update capability

### enrich_with_full_html.py
AI enrichment engine using full HTML content extraction.

**Features:**
- BeautifulSoup HTML parsing
- Claude API integration for analysis
- Relevance scoring (0-10)
- Sentiment analysis
- Keyword extraction
- Market impact assessment

### smart_ai_enrichment_cron.py
Smart batch enrichment for new items only.

**Features:**
- Incremental processing
- Cost optimization
- Automatic scheduling
- Error handling and retries

## Configuration

All API keys should be set as environment variables:
- `ANTHROPIC_API_KEY`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

## Database

Uses LanceDB on S3:
- Bucket: `s3://sage-unified-feed-lance/sage4/`
- Table: `unified_feed`

## Running the Service

```bash
python3 sage4_interface_fixed.py
```

Service will be available at: http://localhost:8540

