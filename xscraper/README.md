# XSCRAPER Source Code

This directory contains the XSCRAPER Twitter and market news monitoring system.

## Main Components

### xscraper_twitter.py
The main Flask application serving the Twitter-like interface on port 8509.

**Key Features:**
- Real-time Twitter feed display
- Market news aggregation
- AI sentiment analysis
- User rating system
- Responsive Twitter-like UI

### xscraper_30min_50tweets.py
Twitter scraping engine using Apify.

**Features:**
- Monitors 35+ financial Twitter accounts
- Fetches 50 tweets every 15 minutes
- Cost-optimized at $72/month
- Automatic deduplication

## Monitored Accounts

### Breaking News
- DeItaone
- FirstSquawk
- LiveSquawk

### Publications
- WSJ
- FT
- Reuters
- CNBC

### Analysis
- zerohedge
- MacroAlf

### Banks
- GoldmanSachs
- JPMorgan

### Analysts
- RaoulGMI
- PeterLBrandt
- spotgamma

## Configuration

Required API keys:
- `APIFY_API_KEY`
- `ANTHROPIC_API_KEY`

## Database

Uses LanceDB on S3:
- Bucket: `s3://sage-unified-feed-lance/tweetss3/`
- Tables: `tweets`, `market_news`

## Running the Service

```bash
python3 xscraper_twitter.py
```

Service will be available at: http://localhost:8509

## Cron Schedule

```bash
# Scrape tweets every 15 minutes
*/15 * * * * python3 xscraper_30min_50tweets.py
```
