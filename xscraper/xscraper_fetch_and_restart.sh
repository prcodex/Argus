#!/bin/bash
# Smart XSCRAPER: Fetch data then restart service

echo "[$(date)] Starting XSCRAPER data fetch and restart cycle..."

# Step 1: Run the data fetch
cd /home/ubuntu/newspaper_project
echo "[$(date)] Fetching new tweets..."
python3 xscraper_30min_50tweets.py >> /home/ubuntu/logs/xscraper_cron.log 2>&1

# Step 2: Wait a moment for database to update
sleep 5

# Step 3: Kill the current XSCRAPER interface
echo "[$(date)] Stopping XSCRAPER interface..."
pkill -f xscraper_twitter.py
sleep 2

# Step 4: Start fresh XSCRAPER interface
echo "[$(date)] Starting fresh XSCRAPER interface..."
nohup python3 xscraper_twitter.py > /home/ubuntu/logs/xscraper_twitter.log 2>&1 &
echo "[$(date)] XSCRAPER restarted with PID: $!"

echo "[$(date)] Cycle complete - fresh interface with new data!"
