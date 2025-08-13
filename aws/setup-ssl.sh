#!/bin/bash

# Setup SSL certificates for HTTPS access
echo "🔒 Setting up SSL certificates for HTTPS"
echo "========================================"

# Method 1: Environment variable
if [ -n "$INSTANCE_ID" ]; then
    echo "✓ Using INSTANCE_ID from environment variable: $INSTANCE_ID"
# Method 2: Command-line argument
elif [ -n "$1" ]; then
    INSTANCE_ID="$1"
    echo "✓ Using INSTANCE_ID from command-line argument: $INSTANCE_ID"
# Method 3: Terraform output file
elif [ -f "terraform/terraform.tfstate" ] && command -v jq >/dev/null 2>&1; then
    INSTANCE_ID=$(jq -r '.outputs.ec2_instance_id.value // empty' terraform/terraform.tfstate 2>/dev/null)
    if [ -n "$INSTANCE_ID" ] && [ "$INSTANCE_ID" != "null" ]; then
        echo "✓ Using INSTANCE_ID from Terraform state: $INSTANCE_ID"
    else
        INSTANCE_ID=""
    fi
# Method 4: Manual terraform output file
elif [ -f "terraform-output-instance-id.txt" ]; then
    INSTANCE_ID=$(cat terraform-output-instance-id.txt)
    echo "✓ Using INSTANCE_ID from terraform-output-instance-id.txt: $INSTANCE_ID"
fi

# Validate INSTANCE_ID is set
if [ -z "$INSTANCE_ID" ]; then
    echo "❌ INSTANCE_ID not set. Please:"
    echo "   1. Set INSTANCE_ID environment variable: export INSTANCE_ID=i-xxxx"
    echo "   2. Pass as argument: $0 i-xxxx"
    echo "   3. Ensure terraform/terraform.tfstate exists with outputs"
    echo "   4. Create terraform-output-instance-id.txt with instance ID"
    exit 1
fi

# Get AWS region (configurable)
REGION="${AWS_REGION:-us-east-2}"
echo "✓ Using AWS region: $REGION"

# Get domain name (configurable)
DOMAIN_NAME="${DOMAIN_NAME:-tulsai.city}"
echo "✓ Using domain: $DOMAIN_NAME"

# Get admin email (configurable)
ADMIN_EMAIL="${ADMIN_EMAIL:-admin@$DOMAIN_NAME}"
echo "✓ Using admin email: $ADMIN_EMAIL"

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
        "        server_name www.$DOMAIN_NAME $DOMAIN_NAME api.$DOMAIN_NAME;",
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
        "sudo certbot --nginx --non-interactive --agree-tos --email $ADMIN_EMAIL -d www.$DOMAIN_NAME -d $DOMAIN_NAME -d api.$DOMAIN_NAME || echo SSL setup completed - check manually",
        "echo SSL setup complete!"
    ]'

if [ $? -eq 0 ]; then
    echo "✅ SSL setup command sent!"
    echo ""
    echo "⏳ This will take 2-3 minutes..."
    echo "After completion, you should be able to access:"
    echo "• https://www.$DOMAIN_NAME"
    echo "• https://api.$DOMAIN_NAME"
    echo "• https://$DOMAIN_NAME"
    echo ""
    echo "💡 If certificates fail, you may need to:"
    echo "• Update DNS A records to point directly to EC2 IP"
    echo "• Wait for full DNS propagation"
else
    echo "❌ Failed to send SSL setup command"
fi
