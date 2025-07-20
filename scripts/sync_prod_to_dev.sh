#!/bin/bash

# Script to safely sync production data to development database
# This is the RECOMMENDED approach vs connecting dev directly to prod

echo "🔄 Syncing Production Data to Development Database"
echo "   This safely copies prod data to your local dev database"
echo "   ✅ Safe: No risk to production data"
echo "   ✅ Fast: Work with real data locally"
echo "   ✅ Offline: No dependency on production availability"
echo ""

# Check if local development database is running
if ! docker ps | grep -q citycamp_postgres; then
    echo "🚀 Starting local development database..."
    docker-compose up postgres redis -d
    echo "⏳ Waiting for database to be ready..."
    sleep 10
fi

# Test production connection
echo "🧪 Testing production database connection..."
if ! PGPASSWORD='CityCamp2005!' psql -h citycamp-ai-db.c8lywk6yg0um.us-east-1.rds.amazonaws.com -U citycamp_user -d postgres -c "SELECT 1;" > /dev/null 2>&1; then
    echo "❌ Cannot connect to production database!"
    exit 1
fi
echo "✅ Production database accessible"

# Test development connection
echo "🧪 Testing development database connection..."
if ! PGPASSWORD=password psql -h localhost -p 5435 -U user -d citycamp_db -c "SELECT 1;" > /dev/null 2>&1; then
    echo "❌ Cannot connect to development database!"
    echo "💡 Try: docker-compose up postgres -d"
    exit 1
fi
echo "✅ Development database accessible"

echo ""
echo "📊 Current data counts:"

# Show production data
echo "Production:"
PGPASSWORD='CityCamp2005!' psql -h citycamp-ai-db.c8lywk6yg0um.us-east-1.rds.amazonaws.com -U citycamp_user -d postgres -t -c "
SELECT
  'Meetings: ' || COUNT(*) FROM meetings
UNION ALL
SELECT
  'Meeting Topics: ' || COUNT(*) FROM meeting_topics
UNION ALL
SELECT
  'Topic Subscriptions: ' || COUNT(*) FROM topic_subscriptions;
"

echo ""
echo "Development (before sync):"
PGPASSWORD=password psql -h localhost -p 5435 -U user -d citycamp_db -t -c "
SELECT
  CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'meetings')
    THEN 'Meetings: ' || (SELECT COUNT(*) FROM meetings)::text
    ELSE 'Meetings: No table found'
  END
UNION ALL
SELECT
  CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'meeting_topics')
    THEN 'Meeting Topics: ' || (SELECT COUNT(*) FROM meeting_topics)::text
    ELSE 'Meeting Topics: No table found'
  END
UNION ALL
SELECT
  CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'topic_subscriptions')
    THEN 'Topic Subscriptions: ' || (SELECT COUNT(*) FROM topic_subscriptions)::text
    ELSE 'Topic Subscriptions: No table found'
  END;
" 2>/dev/null || echo "Development database schema not initialized"

echo ""
read -p "🤔 Proceed with data sync? This will overwrite dev data. (yes/no): " confirm

if [[ $confirm != "yes" ]]; then
    echo "❌ Sync cancelled."
    exit 1
fi

echo ""
echo "🔄 Starting data synchronization..."

# Create temp directory for dumps
mkdir -p /tmp/citycamp_sync

echo "📦 Exporting production data..."

# Export key tables from production
PGPASSWORD='CityCamp2005!' pg_dump \
  -h citycamp-ai-db.c8lywk6yg0um.us-east-1.rds.amazonaws.com \
  -U citycamp_user \
  -d postgres \
  --data-only \
  --inserts \
  -t meetings \
  -t agenda_items \
  -t meeting_categories \
  -t meeting_topics \
  -t topic_subscriptions \
  -t notification_logs \
  > /tmp/citycamp_sync/prod_data.sql

if [ $? -ne 0 ]; then
    echo "❌ Failed to export production data!"
    exit 1
fi

echo "📥 Importing to development database..."

# First, create the schema in dev if it doesn't exist
cd backend
python -c "
from app.core.database import create_tables
create_tables()
print('✅ Database schema updated')
"

# Import the data
PGPASSWORD=password psql -h localhost -p 5435 -U user -d citycamp_db < /tmp/citycamp_sync/prod_data.sql

if [ $? -ne 0 ]; then
    echo "⚠️  Some import warnings occurred (this is often normal)"
fi

# Clean up
rm -rf /tmp/citycamp_sync

echo ""
echo "📊 Data sync complete! New development counts:"
PGPASSWORD=password psql -h localhost -p 5435 -U user -d citycamp_db -t -c "
SELECT
  'Meetings: ' || COUNT(*) FROM meetings
UNION ALL
SELECT
  'Meeting Topics: ' || COUNT(*) FROM meeting_topics
UNION ALL
SELECT
  'Topic Subscriptions: ' || COUNT(*) FROM topic_subscriptions;
"

echo ""
echo "🎉 Development database now has production data!"
echo "💡 Your development environment will now show real meetings data"
echo "🔄 Re-run this script anytime to refresh with latest production data"
