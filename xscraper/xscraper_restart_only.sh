#!/bin/bash
# Restart XSCRAPER interface only (data already fetched and enriched)

echo "[$(date)] Restarting XSCRAPER interface with enriched data..."

# Kill the current XSCRAPER interface
pkill -f xscraper_twitter.py
sleep 2

# Start fresh XSCRAPER interface
cd /home/ubuntu/newspaper_project
nohup python3 xscraper_twitter.py > /home/ubuntu/logs/xscraper_twitter.log 2>&1 &
echo "[$(date)] XSCRAPER restarted with PID: $!"

echo "[$(date)] Fresh interface ready with AI-enriched data!"
