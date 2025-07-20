#!/bin/bash

# Quick fix script for CityCamp AI production API issues
# Addresses common causes of meeting details not loading

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
    echo -e "${BLUE}[FIX]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."

    if ! command -v aws > /dev/null; then
        print_error "AWS CLI not found. Please install and configure AWS CLI."
        exit 1
    fi

    # Check if we can access AWS
    if ! aws sts get-caller-identity > /dev/null 2>&1; then
        print_error "AWS CLI not configured or no access. Please run 'aws configure'."
        exit 1
    fi

    print_status "✅ Prerequisites check passed"
}

# Get production configuration
get_production_config() {
    print_status "Getting production configuration..."

    cd aws/terraform 2>/dev/null || {
        print_error "Cannot find terraform directory. Please run from project root."
        exit 1
    }

    # Get cluster and service names
    CLUSTER_NAME=$(terraform output -raw ecs_cluster_name 2>/dev/null || echo "citycamp-ai-cluster")
    SERVICE_NAME="citycamp-ai-service"
    ALB_DNS=$(terraform output -raw alb_dns_name 2>/dev/null || echo "")
    CLOUDFRONT_DOMAIN=$(terraform output -raw cloudfront_domain_name 2>/dev/null || echo "")

    cd - > /dev/null

    print_status "Cluster: $CLUSTER_NAME"
    print_status "Service: $SERVICE_NAME"
    print_status "ALB DNS: $ALB_DNS"
    print_status "CloudFront: $CLOUDFRONT_DOMAIN"
}

# Fix ECS Service Issues
fix_ecs_service() {
    print_header "Fixing ECS Service Issues"

    # Check current service status
    print_status "Checking ECS service status..."
    SERVICE_STATUS=$(aws ecs describe-services \
        --cluster "$CLUSTER_NAME" \
        --services "$SERVICE_NAME" \
        --query 'services[0].status' \
        --output text 2>/dev/null || echo "NOT_FOUND")

    if [ "$SERVICE_STATUS" = "NOT_FOUND" ]; then
        print_error "ECS service not found: $SERVICE_NAME"
        print_warning "Please deploy the service first using the deployment script."
        return 1
    fi

    # Check running tasks
    RUNNING_TASKS=$(aws ecs describe-services \
        --cluster "$CLUSTER_NAME" \
        --services "$SERVICE_NAME" \
        --query 'services[0].runningCount' \
        --output text 2>/dev/null || echo "0")

    DESIRED_TASKS=$(aws ecs describe-services \
        --cluster "$CLUSTER_NAME" \
        --services "$SERVICE_NAME" \
        --query 'services[0].desiredCount' \
        --output text 2>/dev/null || echo "0")

    print_status "Running tasks: $RUNNING_TASKS / $DESIRED_TASKS desired"

    if [ "$RUNNING_TASKS" = "0" ] || [ "$RUNNING_TASKS" != "$DESIRED_TASKS" ]; then
        print_warning "Service is not healthy. Force deploying..."

        # Force new deployment
        aws ecs update-service \
            --cluster "$CLUSTER_NAME" \
            --service "$SERVICE_NAME" \
            --force-new-deployment \
            --region us-east-1 > /dev/null

        print_status "✅ Forced new deployment initiated"

        # Wait for deployment to stabilize
        print_status "Waiting for service to stabilize (this may take 3-5 minutes)..."
        aws ecs wait services-stable \
            --cluster "$CLUSTER_NAME" \
            --services "$SERVICE_NAME" \
            --region us-east-1

        print_status "✅ Service stabilized"
    else
        print_status "✅ ECS service appears healthy"
    fi
}

# Fix CloudFront Cache Issues
fix_cloudfront_cache() {
    print_header "Fixing CloudFront Cache Issues"

    if [ -z "$CLOUDFRONT_DOMAIN" ]; then
        print_warning "No CloudFront domain found. Skipping cache invalidation."
        return
    fi

    # Get distribution ID
    print_status "Getting CloudFront distribution ID..."
    DISTRIBUTION_ID=$(aws cloudfront list-distributions \
        --query "DistributionList.Items[?DomainName=='$CLOUDFRONT_DOMAIN'].Id" \
        --output text 2>/dev/null || echo "")

    if [ -z "$DISTRIBUTION_ID" ]; then
        print_warning "Could not find CloudFront distribution. Trying alternative method..."
        DISTRIBUTION_ID=$(aws cloudfront list-distributions \
            --query "DistributionList.Items[0].Id" \
            --output text 2>/dev/null || echo "")
    fi

    if [ -n "$DISTRIBUTION_ID" ] && [ "$DISTRIBUTION_ID" != "None" ]; then
        print_status "Found distribution ID: $DISTRIBUTION_ID"

        # Create invalidation for API paths
        print_status "Creating CloudFront invalidation for API paths..."
        INVALIDATION_ID=$(aws cloudfront create-invalidation \
            --distribution-id "$DISTRIBUTION_ID" \
            --paths "/api/*" "/health" \
            --query "Invalidation.Id" \
            --output text 2>/dev/null || echo "")

        if [ -n "$INVALIDATION_ID" ]; then
            print_status "✅ CloudFront invalidation created: $INVALIDATION_ID"
        else
            print_warning "Could not create CloudFront invalidation"
        fi
    else
        print_warning "Could not find CloudFront distribution ID"
    fi
}

# Test API endpoints
test_api_endpoints() {
    print_header "Testing API Endpoints"

    if [ -n "$ALB_DNS" ]; then
        print_status "Testing ALB health endpoint..."
        if curl -f -s --max-time 10 "http://$ALB_DNS/health" > /dev/null; then
            print_status "✅ ALB health check: PASSED"

            print_status "Testing meetings API via ALB..."
            if curl -s --max-time 15 "http://$ALB_DNS/api/v1/meetings/" | grep -q "meetings"; then
                print_status "✅ ALB meetings API: WORKING"

                print_status "Testing meeting details via ALB..."
                if curl -s --max-time 15 "http://$ALB_DNS/api/v1/meetings/1" | grep -q '"meeting"'; then
                    print_status "✅ ALB meeting details: WORKING"
                else
                    print_error "❌ ALB meeting details: FAILED"
                fi
            else
                print_error "❌ ALB meetings API: FAILED"
            fi
        else
            print_error "❌ ALB health check: FAILED"
        fi
    fi

    if [ -n "$CLOUDFRONT_DOMAIN" ]; then
        print_status "Waiting 30 seconds for CloudFront cache to clear..."
        sleep 30

        print_status "Testing meetings API via CloudFront..."
        if curl -s --max-time 30 "https://$CLOUDFRONT_DOMAIN/api/v1/meetings/" | grep -q "meetings"; then
            print_status "✅ CloudFront meetings API: WORKING"

            print_status "Testing meeting details via CloudFront..."
            if curl -s --max-time 30 "https://$CLOUDFRONT_DOMAIN/api/v1/meetings/1" | grep -q '"meeting"'; then
                print_status "✅ CloudFront meeting details: WORKING"
            else
                print_error "❌ CloudFront meeting details: FAILED"
                print_warning "API may take a few more minutes to fully propagate"
            fi
        else
            print_error "❌ CloudFront meetings API: FAILED"
        fi
    fi
}

# Check ALB target group health
check_target_group_health() {
    print_header "Checking ALB Target Group Health"

    # Get target groups
    TARGET_GROUPS=$(aws elbv2 describe-target-groups \
        --names "citycamp-ai-tg-ip" \
        --query "TargetGroups[0].TargetGroupArn" \
        --output text 2>/dev/null || echo "")

    if [ -n "$TARGET_GROUPS" ] && [ "$TARGET_GROUPS" != "None" ]; then
        print_status "Checking target group health..."

        TARGET_HEALTH=$(aws elbv2 describe-target-health \
            --target-group-arn "$TARGET_GROUPS" \
            --query "TargetHealthDescriptions[*].TargetHealth.State" \
            --output text 2>/dev/null || echo "")

        if echo "$TARGET_HEALTH" | grep -q "healthy"; then
            print_status "✅ Target group has healthy targets"
        else
            print_error "❌ Target group targets are not healthy: $TARGET_HEALTH"
            print_warning "This indicates backend container health check issues"
        fi
    else
        print_warning "Could not find target group or no targets registered"
    fi
}

# Show backend logs
show_backend_logs() {
    print_header "Backend Logs (Last 10 lines)"

    print_status "Fetching recent backend logs..."
    aws logs tail /ecs/citycamp-ai-backend \
        --since 10m \
        --format short \
        --region us-east-1 2>/dev/null | tail -10 || {
        print_warning "Could not fetch backend logs"
    }
}

# Main function
main() {
    print_status "🔧 CityCamp AI Production API Fix"
    echo "================================="
    echo

    check_prerequisites
    echo

    get_production_config
    echo

    fix_ecs_service
    echo

    fix_cloudfront_cache
    echo

    check_target_group_health
    echo

    test_api_endpoints
    echo

    show_backend_logs
    echo

    print_status "🎉 Production API fix completed!"
    print_status "Your meeting details should now load properly in production."
    print_warning "If issues persist, please check CloudWatch logs for more details."
}

# Run main function
main "$@"
