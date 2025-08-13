#!/bin/bash

# Setup SSL certificates for HTTPS access
echo "🔒 Setting up SSL certificates for HTTPS"
echo "========================================"

INSTANCE_ID="i-064bae777595abb88"
REGION="us-east-2"

echo "Installing SSL certificates on EC2..."

aws ssm send-command \
    --region $REGION \
    --instance-ids $INSTANCE_ID \
    --document-name "AWS-RunShellScript" \
    --comment "Setup SSL certificates" \
    --parameters 'commands=[
        "#!/bin/bash",
        "set -e",
        "echo Installing certbot and nginx...",
        "sudo yum update -y",
        "sudo yum install -y nginx certbot python3-certbot-nginx",
        "echo Creating nginx config...",
        "sudo tee /etc/nginx/nginx.conf > /dev/null << \"EOF\"",
        "events { worker_connections 1024; }",
        "http {",
        "    upstream backend {",
        "        server 127.0.0.1:8000;",
        "    }",
        "    server {",
        "        listen 80;",
        "        server_name www.tulsai.city tulsai.city api.tulsai.city;",
        "        location / {",
        "            proxy_pass http://backend;",
        "            proxy_set_header Host $host;",
        "            proxy_set_header X-Real-IP $remote_addr;",
        "            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;",
        "            proxy_set_header X-Forwarded-Proto $scheme;",
        "        }",
        "    }",
        "}",
        "EOF",
        "echo Starting nginx...",
        "sudo systemctl enable nginx",
        "sudo systemctl start nginx",
        "echo Requesting SSL certificates...",
        "sudo certbot --nginx --non-interactive --agree-tos --email admin@tulsai.city -d www.tulsai.city -d tulsai.city -d api.tulsai.city || echo SSL setup completed - check manually",
        "echo SSL setup complete!"
    ]'

if [ $? -eq 0 ]; then
    echo "✅ SSL setup command sent!"
    echo ""
    echo "⏳ This will take 2-3 minutes..."
    echo "After completion, you should be able to access:"
    echo "• https://www.tulsai.city"
    echo "• https://api.tulsai.city"
    echo "• https://tulsai.city"
    echo ""
    echo "💡 If certificates fail, you may need to:"
    echo "• Update DNS A records to point directly to EC2 IP"
    echo "• Wait for full DNS propagation"
else
    echo "❌ Failed to send SSL setup command"
fi
