# XSCRAPER Configuration Template
# Copy to xscraper_config.py and update with your values

# API Keys
ANTHROPIC_API_KEY = 'YOUR_ANTHROPIC_API_KEY_HERE'
APIFY_API_KEY = 'YOUR_APIFY_API_KEY_HERE'

# Database
S3_BUCKET = 's3://sage-unified-feed-lance/tweetss3'
TWEETS_TABLE = 'tweets'
NEWS_TABLE = 'market_news'

# Flask Settings
FLASK_PORT = 8509
FLASK_HOST = '0.0.0.0'
FLASK_DEBUG = False

# Timezone
DISPLAY_TIMEZONE = 'America/Sao_Paulo'  # UTC-3

# Twitter Accounts to Monitor
TWITTER_ACCOUNTS = [
    'DeItaone', 'FirstSquawk', 'LiveSquawk',
    'WSJ', 'FT', 'Reuters', 'CNBC',
    'zerohedge', 'MacroAlf', 
    'GoldmanSachs', 'JPMorgan',
    'RaoulGMI', 'PeterLBrandt',
    'spotgamma', 'biancoresearch'
]

# AI Enrichment Settings
AI_MODEL = 'claude-3-haiku-20240307'
AI_MAX_TOKENS = 1500
AI_TEMPERATURE = 0.3

# Refresh Settings (minutes)
FETCH_INTERVAL = 15
AI_PROCESSING_DELAY = 5
