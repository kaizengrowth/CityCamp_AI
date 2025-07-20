#!/bin/bash

# Production API Testing Script for CityCamp AI
# Tests production API endpoints to diagnose meeting details loading issues

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

# Get production endpoints
get_production_endpoints() {
    print_status "Getting production endpoints..."

    cd aws/terraform 2>/dev/null || cd terraform 2>/dev/null || {
        print_error "Cannot find terraform directory. Please run from project root."
        exit 1
    }

    # Get endpoints from Terraform
    ALB_DNS=$(terraform output -raw alb_dns_name 2>/dev/null || echo "")
    CLOUDFRONT_DOMAIN=$(terraform output -raw cloudfront_domain_name 2>/dev/null || echo "")

    cd - > /dev/null

    if [ -z "$ALB_DNS" ] || [ -z "$CLOUDFRONT_DOMAIN" ]; then
        print_error "Could not get production endpoints from Terraform."
        print_warning "Please run: cd aws/terraform && terraform output"
        exit 1
    fi

    print_status "ALB DNS: $ALB_DNS"
    print_status "CloudFront Domain: $CLOUDFRONT_DOMAIN"
}

# Test ALB direct access
test_alb_direct() {
    print_header "Testing ALB Direct Access"

    # Test health check
    print_status "Testing ALB health endpoint..."
    if curl -f -s --max-time 10 "http://$ALB_DNS/health" > /dev/null; then
        print_status "✅ ALB health check: OK"
    else
        print_error "❌ ALB health check: FAILED"
        print_warning "Backend service may not be running"
    fi

    # Test meetings API directly
    print_status "Testing meetings API directly via ALB..."
    ALB_MEETINGS_RESPONSE=$(curl -s --max-time 15 "http://$ALB_DNS/api/v1/meetings/" | head -200)

    if echo "$ALB_MEETINGS_RESPONSE" | grep -q "meetings"; then
        print_status "✅ ALB meetings API: OK"
        MEETING_COUNT=$(echo "$ALB_MEETINGS_RESPONSE" | grep -o '"id":[0-9]*' | wc -l)
        print_status "Found $MEETING_COUNT meetings via ALB"
    else
        print_error "❌ ALB meetings API: FAILED"
        print_warning "Response: $ALB_MEETINGS_RESPONSE"
    fi

    # Test specific meeting details via ALB
    print_status "Testing meeting details directly via ALB..."
    ALB_MEETING_DETAIL_RESPONSE=$(curl -s --max-time 15 "http://$ALB_DNS/api/v1/meetings/1" | head -200)

    if echo "$ALB_MEETING_DETAIL_RESPONSE" | grep -q '"meeting"'; then
        print_status "✅ ALB meeting details: OK"
    else
        print_error "❌ ALB meeting details: FAILED"
        print_warning "Response: $ALB_MEETING_DETAIL_RESPONSE"
    fi
}

# Test CloudFront access
test_cloudfront() {
    print_header "Testing CloudFront Access"

    # Test meetings API via CloudFront
    print_status "Testing meetings API via CloudFront..."
    CF_MEETINGS_RESPONSE=$(curl -s --max-time 30 "https://$CLOUDFRONT_DOMAIN/api/v1/meetings/" | head -200)

    if echo "$CF_MEETINGS_RESPONSE" | grep -q "meetings"; then
        print_status "✅ CloudFront meetings API: OK"
        MEETING_COUNT=$(echo "$CF_MEETINGS_RESPONSE" | grep -o '"id":[0-9]*' | wc -l)
        print_status "Found $MEETING_COUNT meetings via CloudFront"
    else
        print_error "❌ CloudFront meetings API: FAILED"
        print_warning "Response: $CF_MEETINGS_RESPONSE"
    fi

    # Test specific meeting details via CloudFront
    print_status "Testing meeting details via CloudFront..."
    CF_MEETING_DETAIL_RESPONSE=$(curl -s --max-time 30 "https://$CLOUDFRONT_DOMAIN/api/v1/meetings/1" | head -200)

    if echo "$CF_MEETING_DETAIL_RESPONSE" | grep -q '"meeting"'; then
        print_status "✅ CloudFront meeting details: OK"
    else
        print_error "❌ CloudFront meeting details: FAILED"
        print_warning "Response: $CF_MEETING_DETAIL_RESPONSE"
    fi
}

# Test CORS headers
test_cors() {
    print_header "Testing CORS Headers"

    # Test OPTIONS request to CloudFront
    print_status "Testing CORS preflight to CloudFront..."
    CORS_RESPONSE=$(curl -s -I -X OPTIONS \
        -H "Origin: https://$CLOUDFRONT_DOMAIN" \
        -H "Access-Control-Request-Method: GET" \
        -H "Access-Control-Request-Headers: Content-Type" \
        "https://$CLOUDFRONT_DOMAIN/api/v1/meetings/1")

    if echo "$CORS_RESPONSE" | grep -q "Access-Control-Allow"; then
        print_status "✅ CORS headers: OK"
    else
        print_warning "⚠️ CORS headers: May be missing"
        print_warning "Response headers:"
        echo "$CORS_RESPONSE" | grep -i "access-control" || echo "No CORS headers found"
    fi
}

# Check ECS service status
check_ecs_service() {
    print_header "Checking ECS Service Status"

    print_status "Getting ECS service status..."

    # Check if AWS CLI is configured
    if ! command -v aws > /dev/null; then
        print_warning "AWS CLI not found. Skipping ECS checks."
        return
    fi

    # Get cluster name
    CLUSTER_NAME="citycamp-ai-cluster"
    SERVICE_NAME="citycamp-ai-service"

    # Check service status
    SERVICE_STATUS=$(aws ecs describe-services \
        --cluster "$CLUSTER_NAME" \
        --services "$SERVICE_NAME" \
        --query 'services[0].status' \
        --output text 2>/dev/null || echo "NOT_FOUND")

    if [ "$SERVICE_STATUS" = "ACTIVE" ]; then
        print_status "✅ ECS Service: ACTIVE"

        # Check running tasks
        RUNNING_TASKS=$(aws ecs describe-services \
            --cluster "$CLUSTER_NAME" \
            --services "$SERVICE_NAME" \
            --query 'services[0].runningCount' \
            --output text 2>/dev/null || echo "0")

        print_status "Running tasks: $RUNNING_TASKS"

        if [ "$RUNNING_TASKS" = "0" ]; then
            print_error "❌ No running tasks found!"
        fi
    else
        print_error "❌ ECS Service: $SERVICE_STATUS"
    fi
}

# Generate fix recommendations
generate_recommendations() {
    print_header "Fix Recommendations"

    print_status "Based on test results, here are the recommended fixes:"
    echo

    if ! curl -f -s --max-time 10 "http://$ALB_DNS/health" > /dev/null; then
        echo "🔧 Backend Service Issues:"
        echo "   • Check ECS service status: aws ecs describe-services --cluster citycamp-ai-cluster --services citycamp-ai-service"
        echo "   • Check CloudWatch logs: aws logs tail /ecs/citycamp-ai-backend --follow"
        echo "   • Restart ECS service: aws ecs update-service --cluster citycamp-ai-cluster --service citycamp-ai-service --force-new-deployment"
        echo
    fi

    if ! curl -s --max-time 30 "https://$CLOUDFRONT_DOMAIN/api/v1/meetings/1" | grep -q '"meeting"'; then
        echo "🌐 CloudFront Issues:"
        echo "   • Clear CloudFront cache for API paths"
        echo "   • Verify API routing configuration"
        echo "   • Check ALB target group health"
        echo
    fi

    echo "🚀 Quick Fix Commands:"
    echo "   # Force ECS deployment"
    echo "   aws ecs update-service --cluster citycamp-ai-cluster --service citycamp-ai-service --force-new-deployment"
    echo
    echo "   # Clear CloudFront cache"
    echo "   DISTRIBUTION_ID=\$(aws cloudfront list-distributions --query 'DistributionList.Items[0].Id' --output text)"
    echo "   aws cloudfront create-invalidation --distribution-id \$DISTRIBUTION_ID --paths '/api/*'"
    echo
    echo "   # Check backend logs"
    echo "   aws logs tail /ecs/citycamp-ai-backend --follow"
}

# Main function
main() {
    print_status "🔍 CityCamp AI Production API Diagnostics"
    echo "=========================================="
    echo

    get_production_endpoints
    echo

    test_alb_direct
    echo

    test_cloudfront
    echo

    test_cors
    echo

    check_ecs_service
    echo

    generate_recommendations
}

# Run main function
main "$@"
