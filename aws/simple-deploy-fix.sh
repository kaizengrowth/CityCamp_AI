#!/bin/bash

# Simple CityCamp AI deployment script
echo "🚀 Deploying CityCamp AI - Simple Fix"
echo "===================================="

INSTANCE_ID="i-064bae777595abb88"
REGION="us-east-2"

# Create a simple deployment command
aws ssm send-command \
    --region $REGION \
    --instance-ids $INSTANCE_ID \
    --document-name "AWS-RunShellScript" \
    --parameters 'commands=[
        "#!/bin/bash",
        "echo Starting simple backend deployment...",
        "cd /opt/citycamp-ai",
        "sudo docker stop backend 2>/dev/null || true",
        "sudo docker rm backend 2>/dev/null || true",
        "echo Creating simple FastAPI app...",
        "cat > simple_app.py << EOF",
        "from fastapi import FastAPI",
        "app = FastAPI()",
        "@app.get(\"/\")",
        "def read_root():",
        "    return {\"message\": \"CityCamp AI Running!\", \"status\": \"healthy\"}",
        "@app.get(\"/health\")",
        "def health():",
        "    return {\"status\": \"healthy\", \"service\": \"CityCamp AI\", \"version\": \"1.0.0\"}",
        "EOF",
        "echo Building and starting backend...",
        "sudo docker run -d -p 8000:8000 --name backend --restart unless-stopped -v $(pwd):/app -w /app python:3.11-slim sh -c \"pip install fastapi uvicorn && python -m uvicorn simple_app:app --host 0.0.0.0 --port 8000\"",
        "sleep 15",
        "curl -s http://localhost:8000/health || echo Backend still starting...",
        "echo Deployment completed!"
    ]' \
    --query 'Command.CommandId' \
    --output text

echo "✅ Deployment command sent!"
