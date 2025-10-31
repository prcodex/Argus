#!/bin/bash
# SAGE 4.0 Startup Script
# Single database architecture with infinite flexibility

echo "================================================"
echo "       SAGE 4.0 - Single Database System       "
echo "================================================"
echo ""
echo "Features:"
echo "  ✅ Single LanceDB instance (no more SQLite!)"
echo "  ✅ Infinite flexibility via custom_fields"
echo "  ✅ No schema migrations ever needed"
echo "  ✅ Support for Twitter, LinkedIn, Reddit, etc."
echo ""

# Check if migration is needed
if python3 -c "import lancedb; db = lancedb.connect('s3://sage-unified-feed-lance/sage4/'); t = db.open_table('unified_feed')" 2>/dev/null; then
    echo "✅ SAGE 4.0 database exists"
else
    echo "⚠️  SAGE 4.0 database not found"
    echo ""
    read -p "Would you like to run the migration from SAGE 3.0? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Running migration..."
        python3 /home/ubuntu/newspaper_project/migrate_sage3_to_sage4.py
        if [ $? -ne 0 ]; then
            echo "❌ Migration failed. Please check the logs."
            exit 1
        fi
    else
        echo "Skipping migration. Starting with existing data (if any)."
    fi
fi

echo ""
echo "Starting SAGE 4.0 Interface..."
echo "URL: http://44.250.178.165:8540/"
echo ""

# Kill any existing process on port 8540
lsof -ti:8540 | xargs kill -9 2>/dev/null

# Start SAGE 4.0
export PORT=8540
python3 /home/ubuntu/newspaper_project/sage4_interface.py


