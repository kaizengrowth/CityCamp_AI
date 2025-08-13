#!/bin/bash

# Configure Production Settings for CityCamp AI
echo "🔧 Configuring Production Settings"
echo "=================================="

INSTANCE_ID="i-064bae777595abb88"
REGION="us-east-2"

echo "Setting up production environment variables..."

# Configure production environment
aws ssm send-command \
    --region $REGION \
    --instance-ids $INSTANCE_ID \
    --document-name "AWS-RunShellScript" \
    --comment "Configure Production Environment" \
    --parameters 'commands=[
        "#!/bin/bash",
        "echo Setting production environment...",
        "sudo docker stop backend || true",
        "sudo docker rm backend || true",
        "cd /opt/app/CityCamp_AI/backend",
        "echo Building with production settings...",
        "sudo docker build -t backend:prod .",
        "echo Starting with production environment...",
        "sudo docker run -d -p 8000:8000 --name backend --restart unless-stopped \\",
        "  -e ENVIRONMENT=production \\",
        "  -e DEBUG=False \\",
        "  -e DATABASE_URL=sqlite:///./data/citycamp.db \\",
        "  -e SECRET_KEY=prod-secret-$(date +%s) \\",
        "  backend:prod",
        "sleep 15",
        "echo Testing production setup...",
        "curl http://localhost:8000/health",
        "echo Configuration complete!"
    ]'

if [ $? -eq 0 ]; then
    echo "✅ Production configuration sent!"
    echo ""
    echo "⏳ Waiting for configuration to complete..."
    sleep 60

    echo "🧪 Testing production setup..."
    RESPONSE=$(curl -s http://www.tulsai.city/health)

    if echo "$RESPONSE" | grep -q "healthy"; then
        echo "✅ SUCCESS! Production environment configured"
        echo ""
        echo "🎯 Your working endpoints:"
        echo "• Main API: http://www.tulsai.city"
        echo "• Health: http://www.tulsai.city/health"
        echo "• Docs: http://api.tulsai.city/docs"
        echo "• Admin: http://api.tulsai.city/admin (if enabled)"

        echo ""
        echo "📊 Current Status:"
        echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"

    else
        echo "⚠️  Configuration may need more time..."
        echo "💡 Check again in 2-3 minutes"
    fi
else
    echo "❌ Failed to send configuration command"
fi

echo ""
echo "🔑 Next Steps (Optional):"
echo "• Add OpenAI API key for chatbot features"
echo "• Deploy frontend (React app)"
echo "• Configure custom domain SSL certificates"
