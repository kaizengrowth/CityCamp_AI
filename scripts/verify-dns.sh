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
echo "Load Balancer IP: $(dig +short citycamp-ai-alb-282921144.us-east-2.elb.amazonaws.com)"
echo "EC2 Instance IP: 3.138.240.133"
echo ""

echo "📋 REQUIRED DNS RECORDS FOR NAMECHEAP:"
echo "Type: A | Host: @   | Value: 3.130.228.109 | TTL: 300"
echo "Type: A | Host: www | Value: 3.130.228.109 | TTL: 300 (REPLACES BROKEN CNAME)"
echo "Type: A | Host: api | Value: 3.130.228.109 | TTL: 300"
echo ""

echo "💡 After DNS changes, wait 5-30 minutes and run this script again."
