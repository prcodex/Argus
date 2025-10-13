#!/bin/bash
# XSCRAPER Deployment Script
echo "Starting XSCRAPER on port 8509..."
cd xscraper
nohup python3 xscraper_twitter.py > xscraper.log 2>&1 &
echo "✅ XSCRAPER started. Check logs at xscraper.log"
