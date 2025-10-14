# XSCRAPER Deployment Guide

## Quick Deploy on AWS EC2

### 1. Install Dependencies
```bash
sudo apt update
sudo apt install python3-pip python3-venv
pip3 install flask pandas lancedb anthropic pytz boto3
```

### 2. Set Environment Variables
```bash
echo 'export ANTHROPIC_API_KEY="your_key"' >> ~/.bashrc
echo 'export APIFY_API_KEY="your_key"' >> ~/.bashrc
source ~/.bashrc
```

### 3. Configure AWS Security Group
Open ports in AWS Console:
- Port 8509 (XSCRAPER Interface)
- Source: 0.0.0.0/0 (or restrict to your IP)

### 4. Start Service
```bash
cd /home/ubuntu/xscraper
nohup python3 xscraper_twitter.py > logs/xscraper.log 2>&1 &
```

### 5. Set Up Cron Jobs
```bash
crontab -e

# Add these lines:
0,15,30,45 * * * * cd /home/ubuntu/xscraper && python3 xscraper_30min_50tweets.py >> logs/fetch.log 2>&1
5,20,35,50 * * * * /home/ubuntu/xscraper/xscraper_restart_only.sh >> logs/restart.log 2>&1
```

### 6. Verify
- Check interface: http://your-server-ip:8509
- Check logs: tail -f logs/xscraper.log
- Check cron: crontab -l

## Troubleshooting

### Interface not refreshing?
1. Check cron jobs are running
2. Verify API keys are set
3. Check logs for errors
4. Try manual restart: `pkill -f xscraper_twitter.py && python3 xscraper_twitter.py`

### Ratings not persisting?
1. Check user_ratings.json exists and is writable
2. Verify Flask can read/write to the file
3. Check browser console for JavaScript errors

### AI enrichment missing?
1. Verify ANTHROPIC_API_KEY is set
2. Check API quota/billing
3. Look for enrichment errors in logs
