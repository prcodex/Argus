# 🚀 ARGUS - Unified Intelligence System

## Overview
ARGUS is a comprehensive financial intelligence platform combining two powerful systems:
- **SAGE AI** (Port 8540): Advanced email and news aggregation with AI enrichment
- **XSCRAPER** (Port 8509): Real-time Twitter and market news monitoring

## 📊 System Architecture

### SAGE AI (Port 8540)
**Purpose**: Intelligent email and news feed aggregation with AI-powered analysis

#### Key Features:
- **AI Enrichment**: Relevance scoring (0-10), sentiment analysis, keyword extraction
- **Sender Detection**: Automatic categorization of 290+ sources
- **User Ratings**: Personal rating system alongside AI scores
- **Blocked Senders**: Pattern-based filtering system
- **Beautiful HTML Display**: Gmail-like interface for emails
- **Auto-refresh**: Updates every 2 minutes

#### Components:
```
sage_ai/
├── sage4_interface_fixed.py       # Main Flask backend
├── sage_4.0_interface.html        # Main UI template
├── sage_config.html               # Sender configuration page
├── comprehensive_sender_update.py # Sender detection logic
├── enrich_with_full_html.py      # AI enrichment engine
├── smart_ai_enrichment_cron.py   # Smart batch enrichment
└── sage4_cron_robust.sh          # Gmail fetcher script
```

#### Data Flow:
1. **Email Ingestion**: Gmail IMAP → Fetch emails every 30 minutes
2. **Sender Detection**: Categorize by domain/pattern
3. **Blocking Check**: Filter against blocked patterns
4. **AI Analysis**: Extract keywords, sentiment, relevance
5. **Storage**: LanceDB on S3 (s3://sage-unified-feed-lance/sage4/)
6. **Display**: Web interface with filters and search

#### API Endpoints:
- `GET /api/feed` - Main feed with filters
- `GET /api/sender-stats` - Sender statistics
- `POST /api/block-sender` - Add blocked pattern
- `GET /api/blocked-senders` - List blocked patterns
- `POST /api/unblock-sender` - Remove blocked pattern
- `POST /api/set_user_rating` - Set user rating
- `GET /config` - Sender configuration page

### XSCRAPER (Port 8509)
**Purpose**: Real-time Twitter and market news aggregation

#### Key Features:
- **Twitter Monitoring**: 35+ financial accounts
- **Market News**: 7+ major news sources
- **AI Sentiment**: Real-time sentiment analysis
- **User Ratings**: 5-star rating system
- **Twitter-like Interface**: Familiar, responsive design
- **Cost-Optimized**: $72/month total operation

#### Components:
```
xscraper/
├── xscraper_twitter.py            # Main Flask application
├── twitter.html                   # Twitter-like UI
├── xscraper_30min_50tweets.py    # Tweet scraper (Apify)
├── xscraper_smart_news.py        # News aggregator
├── deploy_twitter.sh             # Deployment script
└── monitor_xscraper.sh           # Health monitoring
```

#### Monitored Sources:
**Twitter Accounts** (35 total):
- Breaking News: DeItaone, FirstSquawk, LiveSquawk
- Publications: WSJ, FT, Reuters, CNBC
- Analysis: zerohedge, MacroAlf
- Banks: GoldmanSachs, JPMorgan
- Analysts: RaoulGMI, PeterLBrandt

**News Sources**:
- Bloomberg, Reuters, CNBC, MarketWatch
- Financial Times, WSJ, Yahoo Finance

## 🔄 Automation & Cron Jobs

### SAGE AI Cron Schedule:
```bash
# Gmail fetcher - Every 30 minutes
*/30 * * * * sage4_cron_robust.sh

# Sender detection & AI enrichment - Every 30 minutes
*/30 * * * * enhanced_sage_cron.sh

# Smart AI enrichment (new items only) - Hourly at :15
15 * * * * smart_ai_enrichment_cron.py

# Log cleanup - Daily at 3 AM
0 3 * * * find logs/ -mtime +7 -delete
```

### XSCRAPER Cron Schedule:
```bash
# Twitter scraping - Every 15 minutes
*/15 * * * * xscraper_30min_50tweets.py

# Smart news scraper - Every 2 hours
0 */2 * * * xscraper_smart_news.py

# Interface monitor - Every 5 minutes
*/5 * * * * monitor_xscraper.sh
```

## 📈 Database Architecture

### LanceDB on S3:
- **SAGE**: `s3://sage-unified-feed-lance/sage4/`
  - Table: `unified_feed` (290+ items)
  - Table: `blocked_senders` (pattern filters)
  
- **XSCRAPER**: `s3://sage-unified-feed-lance/tweetss3/`
  - Table: `tweets` (670+ items)
  - Table: `market_news` (300+ items)

## 🛠️ Installation & Setup

### Prerequisites:
```bash
# Python 3.8+
pip install flask pandas lancedb anthropic beautifulsoup4 pytz

# AWS credentials configured
aws configure

# API Keys needed (set as environment variables):
export ANTHROPIC_API_KEY="YOUR_KEY"
export APIFY_API_KEY="YOUR_KEY"
```

### Quick Start:
```bash
# 1. Clone the repository
git clone https://github.com/prcodex/Argus.git
cd Argus

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure API keys
cp .env.example .env
# Edit .env with your keys

# 4. Start SAGE AI
cd sage_ai
python3 sage4_interface_fixed.py

# 5. Start XSCRAPER (in new terminal)
cd xscraper
python3 xscraper_twitter.py
```

## 🔐 Security & Configuration

### API Keys (Required):
- **Anthropic API**: For AI analysis (Claude Haiku)
- **Apify API**: For Twitter scraping
- **AWS Credentials**: For S3 LanceDB access
- **Gmail App Password**: For email fetching

### Blocked Senders Configuration:
Access `/config` endpoint to manage blocked patterns:
- Exact email: `spam@example.com`
- Domain: `*@bloomberg.com`
- Keyword: `*newsletter*@*`
- Subdomain: `*@*.example.com`

## 📊 Performance Metrics

### SAGE AI:
- **Processing**: ~50 emails/minute
- **AI Enrichment**: $0.001 per item
- **Storage**: Unlimited (S3-backed)
- **Latency**: <100ms API response

### XSCRAPER:
- **Tweet Collection**: 50 tweets/15 minutes
- **Cost**: $72/month total
- **Sentiment Analysis**: Real-time
- **Storage**: 970+ items retained

## 🚨 Monitoring & Logs

### Log Locations:
```
/logs/sage4_cron.log          # Gmail fetcher logs
/logs/smart_enrichment.log    # AI enrichment logs
/logs/xscraper_30min.log      # Twitter scraping logs
/logs/xscraper_monitor.log    # Health check logs
```

### Health Checks:

#### Local:
- SAGE AI: `http://localhost:8540/api/feed`
- XSCRAPER: `http://localhost:8509/api/feed`

#### Production (AWS):
- SAGE AI: `http://44.225.226.126:8540/api/feed`
- XSCRAPER: `http://44.225.226.126:8509/api/feed`

## 📝 API Documentation

### SAGE AI Filters:
```javascript
// Get Goldman Sachs emails
GET /api/feed?type=sender:Goldman%20Sachs

// Get high relevance items
GET /api/feed?type=relevance:high

// Get positive sentiment
GET /api/feed?type=sentiment:positive
```

### XSCRAPER Filters:
```javascript
// Get tweets only
GET /api/feed?type=tweets

// Get news only
GET /api/feed?type=news

// Get by source
GET /api/feed?source=DeItaone
```

## 🔄 Backup & Recovery

### Creating Backups:
```bash
# Backup SAGE
tar -czf sage_backup.tar.gz sage_ai/

# Backup XSCRAPER
tar -czf xscraper_backup.tar.gz xscraper/

# Backup databases (metadata only, data is on S3)
crontab -l > cron_backup.txt
```

### Restoration:
```bash
# Extract backups
tar -xzf sage_backup.tar.gz
tar -xzf xscraper_backup.tar.gz

# Restore cron
crontab cron_backup.txt

# Start services
./deploy_sage.sh
./deploy_twitter.sh
```

## 📈 Future Enhancements

- [ ] Machine Learning for pattern detection
- [ ] Advanced filtering with RegEx
- [ ] Mobile app integration
- [ ] WebSocket for real-time updates
- [ ] Multi-user support with authentication
- [ ] Advanced analytics dashboard
- [ ] Export to Excel/CSV
- [ ] Webhook integrations

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is proprietary software. All rights reserved.

## 👤 Author

**Pedro Ribeiro**
- GitHub: [@prcodex](https://github.com/prcodex)
- Repository: [Argus](https://github.com/prcodex/Argus)

## 🌐 Production Server

**AWS Elastic IP**: `44.225.226.126` (Permanent - will not change)
- **SAGE AI**: http://44.225.226.126:8540
- **XSCRAPER**: http://44.225.226.126:8509

## 🙏 Acknowledgments

- Anthropic for Claude AI
- Apify for web scraping
- AWS for infrastructure  
- LanceDB for vector storage

---
*Last Updated: October 13, 2025*
*Version: 1.0.1*
