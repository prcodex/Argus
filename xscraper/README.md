# XSCRAPER - Financial Intelligence Feed (October 2025 Edition)

## 🚀 Features

### Beautiful Twitter-like Interface
- Real-time financial news aggregation from 35+ Twitter accounts
- Market news from 7 major sources
- Clean, modern UI with UTC-3 (Brazil/São Paulo) timezone

### AI Enrichment
- **Relevance Score**: 0-10 AI rating for market importance
- **Sentiment Analysis**: Positive/Negative/Neutral with color coding
- **Keywords**: Extracted key terms as blue bubbles
- **Categories**: Earnings, Macro Data, Central Bank, Market Movement, etc.
- **Market Impact**: High/Medium/Low assessment

### User Rating System
- **Persistent Ratings**: Your ratings are saved permanently
- **Dual Score Display**: Shows both 👤 User and 🤖 AI scores
- **Visual Rating**: 5-star system with numeric input
- **Instant Save**: Ratings persist through refreshes and restarts

### Smart Auto-Refresh (October 2025)
- **Server-side restart** every 15 minutes for clean state
- **5-minute AI processing gap** ensures full enrichment
- **No JavaScript issues** - server handles everything
- **Beautiful countdown timer** shows next update

## 📊 Data Sources

### Twitter Accounts (35)
- Breaking News: DeItaone, FirstSquawk, LiveSquawk
- Publications: WSJ, FT, Reuters, CNBC
- Analysis: zerohedge, MacroAlf
- Banks: GoldmanSachs, JPMorgan
- Analysts: RaoulGMI, PeterLBrandt
- Market Data: spotgamma, biancoresearch

### Market News (7 sources)
- International and Brazilian financial news
- Real-time market updates
- Economic indicators

## 🔧 Technical Architecture

### Backend
- **Flask** web framework (Python)
- **LanceDB** on S3 for data storage
- **Claude 3.5 Haiku** for AI enrichment ($0.0001/item)
- **Apify** for Twitter scraping ($72/month)

### Frontend  
- **Server-side rendering** for instant display
- **AJAX updates** for dynamic content
- **Brazil timezone** (UTC-3) for timestamps
- **Responsive design** for mobile/desktop

### Automation
```bash
# Cron schedule (every 15 minutes)
0,15,30,45 * * * * fetch tweets + AI enrichment
5,20,35,50 * * * * restart interface with enriched data
```

## 💰 Operating Costs
- Apify Twitter scraping: $57.60/month
- Claude AI enrichment: $14.40/month
- **Total**: $72/month

## 🛠️ Installation

### Requirements
```bash
pip install flask pandas lancedb anthropic pytz
```

### Environment Variables
```bash
export ANTHROPIC_API_KEY='your_key_here'
export APIFY_API_KEY='your_key_here'
```

### Start Service
```bash
# Manual start
python3 xscraper_twitter.py

# With auto-restart (recommended)
./xscraper_fetch_and_restart.sh
```

### Cron Setup
```bash
# Add to crontab
0,15,30,45 * * * * cd /path/to/xscraper && python3 xscraper_30min_50tweets.py
5,20,35,50 * * * * /path/to/xscraper/xscraper_restart_only.sh
```

## 📈 Performance

- **50 tweets** fetched every 15 minutes
- **670+ tweets** in database
- **300+ articles** in market news table
- **98% uptime** with auto-restart system
- **2-second** page load time

## 🎯 October 2025 Improvements

1. **Smart Restart System**: Server restarts after data fetch
2. **AI Enrichment Timing**: 5-minute gap for processing
3. **User Rating Persistence**: Ratings saved to JSON
4. **Dual Score Display**: Both AI and User ratings
5. **Brazil Timezone**: UTC-3 for local time
6. **Visual Countdown**: Shows time to next update
7. **Clean State**: Every refresh like first load

## 📝 License

Part of the ARGUS Intelligence System - October 2025
