#!/bin/bash

# Route 53 DNS Update Script for tulsai.city
echo "🔧 Updating Route 53 DNS records for tulsai.city"
echo "==============================================="
echo ""

HOSTED_ZONE_ID="Z00825362FJ8FZMZBHMBR"
CHANGE_BATCH_FILE="aws/route53-dns-update.json"
LOAD_BALANCER_IP="3.130.228.109"

echo "Configuration:"
echo "• Hosted Zone ID: $HOSTED_ZONE_ID"
echo "• Load Balancer IP: $LOAD_BALANCER_IP"
echo "• Records to update: @ (root), www, api"
echo ""

# Check if change batch file exists
if [ ! -f "$CHANGE_BATCH_FILE" ]; then
    echo "❌ Change batch file not found: $CHANGE_BATCH_FILE"
    echo "💡 Run this script from the project root directory"
    exit 1
fi

echo "🚀 Submitting DNS changes to Route 53..."

# Submit the change batch
CHANGE_ID=$(aws route53 change-resource-record-sets \
    --hosted-zone-id "$HOSTED_ZONE_ID" \
    --change-batch file://"$CHANGE_BATCH_FILE" \
    --query 'ChangeInfo.Id' \
    --output text)

if [ $? -eq 0 ]; then
    echo "✅ DNS change submitted successfully!"
    echo "📋 Change ID: $CHANGE_ID"
    echo ""
    echo "⏳ Monitoring change status..."

    # Wait for change to propagate
    aws route53 wait resource-record-sets-changed --id "$CHANGE_ID"

    if [ $? -eq 0 ]; then
        echo "✅ DNS changes have propagated!"
        echo ""
        echo "🎯 Updated records:"
        echo "• tulsai.city → $LOAD_BALANCER_IP"
        echo "• www.tulsai.city → $LOAD_BALANCER_IP"
        echo "• api.tulsai.city → $LOAD_BALANCER_IP"
        echo ""
        echo "🔍 Test your domains:"
        echo "• curl -I http://tulsai.city"
        echo "• curl -I http://www.tulsai.city"
        echo "• curl -I http://api.tulsai.city"
    else
        echo "⚠️  Change submitted but propagation status unknown"
        echo "💡 Check manually in AWS Console or wait 5-10 minutes"
    fi
else
    echo "❌ Failed to submit DNS changes"
    echo "💡 Check your AWS credentials and permissions"
    exit 1
fi

echo ""
echo "🎉 DNS migration complete! CloudFront outage resolved."
