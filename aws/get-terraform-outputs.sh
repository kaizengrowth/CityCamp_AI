#!/bin/bash

# Helper script to extract Terraform outputs for use with other AWS scripts
echo "📋 Extracting Terraform Outputs"
echo "==============================="

TERRAFORM_DIR="${1:-terraform}"

if [ ! -f "$TERRAFORM_DIR/terraform.tfstate" ]; then
    echo "❌ Terraform state file not found: $TERRAFORM_DIR/terraform.tfstate"
    echo "💡 Run this script from the aws/ directory or specify terraform directory:"
    echo "   $0 /path/to/terraform/directory"
    exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
    echo "❌ jq command not found. Please install jq to parse JSON outputs."
    echo "💡 Install with: brew install jq (macOS) or apt-get install jq (Ubuntu)"
    exit 1
fi

echo "📁 Using Terraform state: $TERRAFORM_DIR/terraform.tfstate"
echo ""

# Extract key outputs
INSTANCE_ID=$(jq -r '.outputs.ec2_instance_id.value // "null"' "$TERRAFORM_DIR/terraform.tfstate")
PUBLIC_IP=$(jq -r '.outputs.ec2_public_ip.value // "null"' "$TERRAFORM_DIR/terraform.tfstate")
ALB_DNS_NAME=$(jq -r '.outputs.alb_dns_name.value // "null"' "$TERRAFORM_DIR/terraform.tfstate")
VPC_ID=$(jq -r '.outputs.vpc_id.value // "null"' "$TERRAFORM_DIR/terraform.tfstate")

echo "🖥️  EC2 Instance ID: $INSTANCE_ID"
echo "🌐 EC2 Public IP: $PUBLIC_IP"
echo "⚖️  ALB DNS Name: $ALB_DNS_NAME"
echo "🔗 VPC ID: $VPC_ID"
echo ""

# Save outputs to files for script consumption
if [ "$INSTANCE_ID" != "null" ]; then
    echo "$INSTANCE_ID" > terraform-output-instance-id.txt
    echo "💾 Saved instance ID to: terraform-output-instance-id.txt"
fi

if [ "$PUBLIC_IP" != "null" ]; then
    echo "$PUBLIC_IP" > terraform-output-public-ip.txt
    echo "💾 Saved public IP to: terraform-output-public-ip.txt"
fi

if [ "$ALB_DNS_NAME" != "null" ]; then
    echo "$ALB_DNS_NAME" > terraform-output-alb-dns.txt
    echo "💾 Saved ALB DNS to: terraform-output-alb-dns.txt"
fi

echo ""
echo "🚀 Usage with other scripts:"
echo "   INSTANCE_ID=\$(cat terraform-output-instance-id.txt) ./setup-ssl.sh"
echo "   EC2_IP=\$(cat terraform-output-public-ip.txt) ../scripts/verify-dns.sh"
echo "   ALB_DNS_NAME=\$(cat terraform-output-alb-dns.txt) ../scripts/verify-dns.sh"
echo ""
echo "✅ Terraform outputs extracted successfully!"
