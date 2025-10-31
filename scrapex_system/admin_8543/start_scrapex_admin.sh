#!/bin/bash
# Start SCRAPEX Admin Interface on port 8543

cd /home/ubuntu/newspaper_project

# Kill existing
pkill -f "scrapex_admin.py"

# Start fresh
nohup python3 scrapex_admin.py > /home/ubuntu/logs/scrapex_admin.log 2>&1 &

echo "✅ SCRAPEX Admin started on port 8543"
echo "   Access: http://44.225.226.126:8543"
echo ""
echo "Features:"
echo "  • Manage allowed senders"
echo "  • View tag mappings"
echo "  • Test tagging logic"
echo "  • View handler details"
echo ""
