#!/usr/bin/env python3
"""
XSCRAPER - PRODUCTION CRON JOB WITH AI ENRICHMENT
Fetches latest 50 tweets every 30 minutes + enriches with Claude Haiku 3.5
"""

import json
import lancedb
import pyarrow as pa
from datetime import datetime
from apify_client import ApifyClient
from anthropic import Anthropic
import os
import pytz
import uuid
import configparser
import pandas as pd
import time

# Setup
et_tz = pytz.timezone('US/Eastern')
anthropic_client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

print("=" * 70)
print("🚀 XSCRAPER 30-Minute Tweet Update + AI Enrichment")
print(f"⏰ {datetime.now(et_tz).strftime('%Y-%m-%d %I:%M %p ET')}")
print("=" * 70)

def enrich_tweet_quick(tweet_text: str, username: str) -> dict:
    """Quick enrichment using Claude Haiku 3.5"""
    prompt = f"""Analyze this financial tweet and extract JSON data.

Tweet from @{username}: {tweet_text}

Return ONLY JSON (no markdown):
{{"keywords": ["term1", "term2"], "main_actors": {{"people": [], "organizations": [], "tickers": [], "countries": []}}, "ai_enrichment": {{"relevance_score": 5, "category": "other", "sentiment": "neutral", "market_impact": "low", "reasoning": "brief reason"}}}}"""

    try:
        response = anthropic_client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=512,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        result = response.content[0].text.strip()
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]
        enrichment = json.loads(result.strip())
        enrichment['ai_enrichment']['enriched_at'] = datetime.now(pytz.UTC).isoformat()
        enrichment['ai_enrichment']['model'] = 'claude-3-5-haiku-20241022'
        return enrichment
    except Exception as e:
        return {
            "keywords": [],
            "main_actors": {"people": [], "organizations": [], "tickers": [], "countries": []},
            "ai_enrichment": {
                "relevance_score": 0,
                "category": "other",
                "sentiment": "neutral",
                "market_impact": "low",
                "reasoning": f"Error: {str(e)[:50]}",
                "enriched_at": datetime.now(pytz.UTC).isoformat(),
                "model": "claude-3-5-haiku-20241022"
            }
        }

# Connect to database
print("\n1️⃣ Connecting to LanceDB on S3...")
aws_key = os.environ.get("AWS_ACCESS_KEY_ID")
aws_secret = os.environ.get("AWS_SECRET_ACCESS_KEY")

if not aws_key or not aws_secret:
    cred_path = os.path.expanduser("~/.aws/credentials")
    config = configparser.ConfigParser()
    config.read(cred_path)
    if 'default' in config:
        aws_key = config['default']['aws_access_key_id']
        aws_secret = config['default']['aws_secret_access_key']

db = lancedb.connect(
    "s3://sage-unified-feed-lance/tweetss3",
    storage_options={
        "aws_access_key_id": aws_key,
        "aws_secret_access_key": aws_secret,
        "region": "us-west-2"
    }
)

tweets_table = db.open_table("tweets")
print("✅ Connected to database")

# Get existing tweet IDs
print("\n2️⃣ Loading existing tweet IDs...")
try:
    existing_df = tweets_table.search().limit(10000).to_pandas()
    existing_ids = set(existing_df['id'].tolist()) if not existing_df.empty else set()
    print(f"✅ Found {len(existing_ids)} existing tweets")
except:
    existing_ids = set()
    print("⚠️ Starting fresh")

# Fetch tweets
print("\n3️⃣ Fetching latest 50 tweets...")
client = ApifyClient("YOUR_APIFY_API_KEY_HERE")
list_url = "https://x.com/i/lists/1955968749036572718"

run_input = {
    "startUrls": [list_url],
    "maxItems": 50,
    "sort": "Latest",
    "includeSearchTerms": False
}

print(f"   💰 Expected cost: ~$0.02 (Apify)")

try:
    run = client.actor("61RPP7dywgiy0JPD0").call(run_input=run_input)
    print("✅ Apify run completed")
    
    new_tweets = []
    fetched = 0
    duplicates = 0
    enriched = 0
    
    print("\n4️⃣ Processing and enriching tweets...")
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        fetched += 1
        if fetched > 50:
            break
        
        tweet_id = item.get("id", str(uuid.uuid4()))
        if tweet_id in existing_ids:
            duplicates += 1
            continue
        
        # Parse timestamp
        created_str = item.get("createdAt", item.get("created_at", ""))
        if created_str:
            try:
                created_at = datetime.strptime(created_str, "%a %b %d %H:%M:%S %z %Y")
            except:
                try:
                    created_at = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
                except:
                    created_at = datetime.now(pytz.UTC)
        else:
            created_at = datetime.now(pytz.UTC)
        
        full_text = item.get("full_text") or item.get("text", "")
        author_info = item.get("author", {})
        username = author_info.get("userName", "Unknown")
        
        # AI ENRICHMENT
        print(f"   [{enriched + 1}] Enriching @{username}...")
        enrichment = enrich_tweet_quick(full_text, username)
        enriched += 1
        
        # Extract media URLs
        media = item.get("media", [])
        media_urls = []
        if media:
            for m in media:
                if isinstance(m, dict):
                    url = m.get("media_url_https") or m.get("url", "")
                    if url:
                        media_urls.append(url)
        
        # Build enriched tweet record
        tweet_record = {
            "id": tweet_id,
            "username": username,
            "display_name": author_info.get("name", "Unknown"),
            "text": full_text[:500],
            "created_at": created_at,
            "scraped_at": datetime.now(pytz.UTC),
            "created_at_et": created_at.astimezone(et_tz),
            "likes": item.get("likeCount", 0),
            "retweets": item.get("retweetCount", 0),
            "replies": item.get("replyCount", 0),
            "media_urls": json.dumps(media_urls),
            # AI ENRICHMENT FIELDS
            "keywords": json.dumps(enrichment['keywords']),
            "main_actors": json.dumps(enrichment['main_actors']),
            "ai_enrichment": json.dumps(enrichment['ai_enrichment'])
        }
        
        new_tweets.append(tweet_record)
        existing_ids.add(tweet_id)
        time.sleep(0.2)  # Rate limiting
    
    print(f"   📊 Fetched: {fetched}")
    print(f"   ✅ New: {len(new_tweets)}")
    print(f"   🤖 Enriched: {enriched}")
    print(f"   🔄 Duplicates: {duplicates}")
    
    # Save to database
    if new_tweets:
        print(f"\n5️⃣ Saving {len(new_tweets)} enriched tweets...")
        df = pd.DataFrame(new_tweets)
        tweets_table.add(df)
        print(f"✅ Saved successfully")
        
        # Cost estimate
        apify_cost = fetched * 0.0004
        ai_cost = enriched * 0.0001
        total_cost = apify_cost + ai_cost
        print(f"   💰 Cost: Apify ${apify_cost:.4f} + AI ${ai_cost:.4f} = ${total_cost:.4f}")
    else:
        print(f"\n5️⃣ No new tweets to save")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print(f"✅ Complete at {datetime.now(et_tz).strftime('%I:%M %p ET')}")
print("=" * 70)
