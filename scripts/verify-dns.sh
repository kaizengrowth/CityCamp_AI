#!/bin/bash

# DNS Verification Script for tulsai.city (Updated for CloudFront Outage)
echo "🔍 DNS Verification for tulsai.city - CloudFront Recovery"
echo "========================================================"
echo ""

echo "🚨 ISSUE: CloudFront distribution 'd1s9nkkr0t3pmn.cloudfront.net' was DELETED"
echo "💡 SOLUTION: Point all subdomains to new EC2 infrastructure"
echo ""

echo "1. Checking root domain (tulsai.city):"
dig +short tulsai.city
if [ $? -eq 0 ]; then
    echo "✅ Root domain resolves"
else
    echo "❌ Root domain not resolving yet"
fi
echo ""

echo "2. Checking www subdomain (www.tulsai.city):"
dig +short www.tulsai.city
if [ $? -eq 0 ] && ! dig +short www.tulsai.city | grep -q "cloudfront"; then
    echo "✅ WWW subdomain resolves to new infrastructure"
elif dig +short www.tulsai.city | grep -q "cloudfront"; then
    echo "⚠️  WWW still points to broken CloudFront - UPDATE DNS!"
else
    echo "❌ WWW subdomain not resolving"
fi
echo ""

echo "3. Checking API subdomain (api.tulsai.city):"
dig +short api.tulsai.city
if [ $? -eq 0 ]; then
    echo "✅ API subdomain resolves"
else
    echo "❌ API subdomain not resolving yet"
fi
echo ""

echo "4. Testing HTTP connectivity:"
echo "Root domain:"
curl -I -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://tulsai.city --connect-timeout 10 || echo "❌ Connection failed"

echo "WWW subdomain:"
curl -I -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://www.tulsai.city --connect-timeout 10 || echo "❌ Connection failed"

echo "API subdomain:"
curl -I -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://api.tulsai.city --connect-timeout 10 || echo "❌ Connection failed"
echo ""

echo "5. Current infrastructure status:"

# Try to get ALB DNS name from Terraform outputs first
if [ -f "aws/terraform/terraform.tfstate" ] && command -v jq >/dev/null 2>&1; then
    ALB_DNS_FROM_TF=$(jq -r '.outputs.alb_dns_name.value // empty' aws/terraform/terraform.tfstate 2>/dev/null)
    ALB_DNS_NAME="${ALB_DNS_NAME:-$ALB_DNS_FROM_TF}"
fi

# Fallback to hardcoded value if not found
ALB_DNS_NAME="${ALB_DNS_NAME:-citycamp-ai-alb-282921144.us-east-2.elb.amazonaws.com}"
echo "ALB DNS Name: $ALB_DNS_NAME"
echo "Load Balancer IP: $(dig +short $ALB_DNS_NAME)"

# Try to get EC2 IP from Terraform outputs or environment variable
EC2_IP="${EC2_IP}"
if [ -f "aws/terraform/terraform.tfstate" ] && command -v jq >/dev/null 2>&1 && [ -z "$EC2_IP" ]; then
    EC2_IP=$(jq -r '.outputs.ec2_public_ip.value // empty' aws/terraform/terraform.tfstate 2>/dev/null)
fi
EC2_IP="${EC2_IP:-3.138.240.133}"
echo "EC2 Instance IP: $EC2_IP"
echo ""

echo "📋 REQUIRED DNS RECORDS FOR NAMECHEAP:"
echo "Type: A | Host: @   | Value: $EC2_IP | TTL: 300"
echo "Type: A | Host: www | Value: $EC2_IP | TTL: 300 (REPLACES BROKEN CNAME)"
echo "Type: A | Host: api | Value: $EC2_IP | TTL: 300"
echo ""

echo "💡 After DNS changes, wait 5-30 minutes and run this script again."
