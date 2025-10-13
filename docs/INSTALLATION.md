# ARGUS Installation Guide

## Prerequisites
- Python 3.8 or higher
- AWS account with S3 access
- API keys for Anthropic and Apify

## Step 1: Clone Repository
```bash
git clone https://github.com/prcodex/Argus.git
cd Argus
```

## Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

## Step 3: Configure Environment
```bash
cp configs/env.example .env
# Edit .env with your API keys
```

## Step 4: Initialize Database
```bash
python scripts/init_database.py
```

## Step 5: Start Services
```bash
# Start SAGE AI
./scripts/deploy_sage.sh

# Start XSCRAPER
./scripts/deploy_xscraper.sh
```

## Step 6: Access Interfaces
- SAGE AI: http://localhost:8540
- XSCRAPER: http://localhost:8509

## Troubleshooting
See docs/TROUBLESHOOTING.md for common issues.
