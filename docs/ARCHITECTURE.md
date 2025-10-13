# ARGUS System Architecture

## Overview
```
┌─────────────────────────────────────────┐
│              ARGUS SYSTEM                │
├─────────────┬───────────────────────────┤
│   SAGE AI   │        XSCRAPER            │
│  Port 8540  │       Port 8509            │
└─────┬───────┴───────────┬────────────────┘
      │                   │
      ▼                   ▼
┌─────────────────────────────────────────┐
│         LanceDB on S3                    │
│  ┌──────────────┬──────────────┐        │
│  │ sage4/       │ tweetss3/    │        │
│  │ unified_feed │ tweets       │        │
│  │              │ market_news  │        │
│  └──────────────┴──────────────┘        │
└─────────────────────────────────────────┘
```

## Data Flow

### SAGE AI Pipeline
1. **Gmail Fetch** → Every 30 minutes
2. **Sender Detection** → Categorize sources
3. **Blocking Check** → Filter unwanted
4. **AI Enrichment** → Extract insights
5. **Store to LanceDB** → S3 persistence
6. **Web Interface** → User access

### XSCRAPER Pipeline
1. **Apify Scraper** → Every 15 minutes
2. **Tweet Collection** → 50 tweets/run
3. **News Aggregation** → Multiple sources
4. **Sentiment Analysis** → Real-time
5. **Store to LanceDB** → S3 persistence
6. **Twitter UI** → User access

## Components

### Backend Services
- Flask (Python web framework)
- LanceDB (Vector database)
- Anthropic Claude (AI analysis)
- Apify (Web scraping)

### Frontend
- HTML5/CSS3/JavaScript
- Material Design Icons
- Responsive design
- Auto-refresh capability

### Storage
- AWS S3 (Primary storage)
- LanceDB tables (Indexed data)
- JSON files (User preferences)
