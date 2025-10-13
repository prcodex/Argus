"""
XSCRAPER Configuration Sample
Replace API keys with your actual values
"""

# API Configuration
APIFY_API_KEY = "YOUR_APIFY_API_KEY_HERE"
ANTHROPIC_API_KEY = "YOUR_ANTHROPIC_API_KEY_HERE"

# Database Configuration
LANCEDB_S3_PATH = "s3://your-bucket/tweetss3/"

# Twitter Accounts to Monitor
TWITTER_ACCOUNTS = [
    "DeItaone", "FirstSquawk", "LiveSquawk",
    "WSJ", "FT", "Reuters", "CNBC",
    "zerohedge", "MacroAlf", "GoldmanSachs"
]

# Service Configuration
PORT = 8509
REFRESH_INTERVAL = 15  # minutes
