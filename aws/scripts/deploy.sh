#!/bin/bash

# AWS Deployment Script for CityCamp AI
# This script automates the deployment process to AWS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="citycamp-ai"
AWS_REGION="us-east-1"
ECR_REPOSITORY_BACKEND="${PROJECT_NAME}-backend"
ECR_REPOSITORY_FRONTEND="${PROJECT_NAME}-frontend"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."

    if ! command_exists aws; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi

    if ! command_exists docker; then
        print_error "Docker is not installed. Please install it first."
        exit 1
    fi

    if ! command_exists terraform; then
        print_error "Terraform is not installed. Please install it first."
        exit 1
    fi

    # Check AWS credentials
    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        print_error "AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    fi

    print_status "Prerequisites check passed!"
}

# Get AWS account ID
get_account_id() {
    aws sts get-caller-identity --query Account --output text
}

# Create ECR repositories
create_ecr_repositories() {
    print_status "Creating ECR repositories..."

    local account_id=$(get_account_id)

    # Create backend repository
    if ! aws ecr describe-repositories --repository-names "$ECR_REPOSITORY_BACKEND" --region "$AWS_REGION" >/dev/null 2>&1; then
        aws ecr create-repository --repository-name "$ECR_REPOSITORY_BACKEND" --region "$AWS_REGION"
        print_status "Created ECR repository: $ECR_REPOSITORY_BACKEND"
    else
        print_status "ECR repository already exists: $ECR_REPOSITORY_BACKEND"
    fi

    # Create frontend repository
    if ! aws ecr describe-repositories --repository-names "$ECR_REPOSITORY_FRONTEND" --region "$AWS_REGION" >/dev/null 2>&1; then
        aws ecr create-repository --repository-name "$ECR_REPOSITORY_FRONTEND" --region "$AWS_REGION"
        print_status "Created ECR repository: $ECR_REPOSITORY_FRONTEND"
    else
        print_status "ECR repository already exists: $ECR_REPOSITORY_FRONTEND"
    fi
}

# Build and push Docker images
build_and_push_images() {
    print_status "Building and pushing Docker images..."

    local account_id=$(get_account_id)
    local ecr_backend_uri="${account_id}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY_BACKEND}"
    local ecr_frontend_uri="${account_id}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY_FRONTEND}"

    # Login to ECR
    aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$ecr_backend_uri"

    # Build and push backend image
    print_status "Building backend image..."
    docker build -t "$ecr_backend_uri:latest" ./backend
    docker push "$ecr_backend_uri:latest"

    # Build and push frontend image
    print_status "Building frontend image..."
    docker build -t "$ecr_frontend_uri:latest" ./frontend
    docker push "$ecr_frontend_uri:latest"

    print_status "Docker images built and pushed successfully!"
}

# Deploy infrastructure with Terraform
deploy_infrastructure() {
    print_status "Deploying infrastructure with Terraform..."

    cd aws/terraform

    # Initialize Terraform
    terraform init

    # Plan the deployment
    terraform plan -out=tfplan

    # Apply the plan
    terraform apply tfplan

    # Get outputs
    ALB_DNS_NAME=$(terraform output -raw alb_dns_name)
    CLOUDFRONT_DOMAIN=$(terraform output -raw cloudfront_domain_name)
    RDS_ENDPOINT=$(terraform output -raw rds_endpoint)
    REDIS_ENDPOINT=$(terraform output -raw redis_endpoint)
    ECS_CLUSTER_NAME=$(terraform output -raw ecs_cluster_name)

    print_status "Infrastructure deployed successfully!"
    print_status "ALB DNS Name: $ALB_DNS_NAME"
    print_status "CloudFront Domain: $CLOUDFRONT_DOMAIN"
    print_status "RDS Endpoint: $RDS_ENDPOINT"
    print_status "Redis Endpoint: $REDIS_ENDPOINT"
    print_status "ECS Cluster: $ECS_CLUSTER_NAME"

    cd ../..
}

# Store secrets in AWS Systems Manager Parameter Store
store_secrets() {
    print_status "Storing secrets in AWS Systems Manager Parameter Store..."

    # Generate a secure secret key if not provided
    if [ -z "$SECRET_KEY" ]; then
        SECRET_KEY=$(openssl rand -hex 32)
        print_warning "Generated new SECRET_KEY. Please save this value securely."
    fi

    # Store secrets
    aws ssm put-parameter --name "/citycamp-ai/database-url" --value "$DATABASE_URL" --type "SecureString" --region "$AWS_REGION" --overwrite
    aws ssm put-parameter --name "/citycamp-ai/redis-url" --value "$REDIS_URL" --type "SecureString" --region "$AWS_REGION" --overwrite
    aws ssm put-parameter --name "/citycamp-ai/secret-key" --value "$SECRET_KEY" --type "SecureString" --region "$AWS_REGION" --overwrite

    # Store optional secrets if provided
    if [ ! -z "$OPENAI_API_KEY" ]; then
        aws ssm put-parameter --name "/citycamp-ai/openai-api-key" --value "$OPENAI_API_KEY" --type "SecureString" --region "$AWS_REGION" --overwrite
    fi

    if [ ! -z "$TWILIO_ACCOUNT_SID" ]; then
        aws ssm put-parameter --name "/citycamp-ai/twilio-account-sid" --value "$TWILIO_ACCOUNT_SID" --type "SecureString" --region "$AWS_REGION" --overwrite
    fi

    if [ ! -z "$TWILIO_AUTH_TOKEN" ]; then
        aws ssm put-parameter --name "/citycamp-ai/twilio-auth-token" --value "$TWILIO_AUTH_TOKEN" --type "SecureString" --region "$AWS_REGION" --overwrite
    fi

    if [ ! -z "$TWILIO_PHONE_NUMBER" ]; then
        aws ssm put-parameter --name "/citycamp-ai/twilio-phone-number" --value "$TWILIO_PHONE_NUMBER" --type "SecureString" --region "$AWS_REGION" --overwrite
    fi

    if [ ! -z "$SMTP_USERNAME" ]; then
        aws ssm put-parameter --name "/citycamp-ai/smtp-username" --value "$SMTP_USERNAME" --type "SecureString" --region "$AWS_REGION" --overwrite
    fi

    if [ ! -z "$SMTP_PASSWORD" ]; then
        aws ssm put-parameter --name "/citycamp-ai/smtp-password" --value "$SMTP_PASSWORD" --type "SecureString" --region "$AWS_REGION" --overwrite
    fi

    print_status "Secrets stored successfully!"
}

# Deploy ECS services
deploy_ecs_services() {
    print_status "Deploying ECS services..."

    local account_id=$(get_account_id)

    # Update task definition with correct account ID and region
    sed "s/ACCOUNT_ID/$account_id/g; s/REGION/$AWS_REGION/g" aws/ecs/task-definition.json > aws/ecs/task-definition-updated.json

    # Register task definition
    aws ecs register-task-definition --cli-input-json file://aws/ecs/task-definition-updated.json --region "$AWS_REGION"

    # Create or update service
    aws ecs create-service \
        --cluster "$ECS_CLUSTER_NAME" \
        --service-name "${PROJECT_NAME}-backend" \
        --task-definition "${PROJECT_NAME}-backend" \
        --desired-count 1 \
        --launch-type FARGATE \
        --network-configuration "awsvpcConfiguration={subnets=[$(aws ecs describe-services --cluster "$ECS_CLUSTER_NAME" --services "${PROJECT_NAME}-backend" --query 'services[0].networkConfiguration.awsvpcConfiguration.subnets' --output text 2>/dev/null || echo 'subnet-12345678,subnet-87654321')],securityGroups=[$(aws ecs describe-services --cluster "$ECS_CLUSTER_NAME" --services "${PROJECT_NAME}-backend" --query 'services[0].networkConfiguration.awsvpcConfiguration.securityGroups' --output text 2>/dev/null || echo 'sg-12345678')],assignPublicIp=DISABLED}" \
        --region "$AWS_REGION" || \
    aws ecs update-service \
        --cluster "$ECS_CLUSTER_NAME" \
        --service "${PROJECT_NAME}-backend" \
        --task-definition "${PROJECT_NAME}-backend" \
        --region "$AWS_REGION"

    print_status "ECS services deployed successfully!"
}

# Deploy frontend to S3
deploy_frontend() {
    print_status "Deploying frontend to S3..."

    # Build frontend for production
    cd frontend
    npm run build

    # Get S3 bucket name from Terraform output
    cd ../aws/terraform
    S3_BUCKET=$(terraform output -raw s3_bucket_name 2>/dev/null || echo "${PROJECT_NAME}-frontend")
    cd ../..

    # Sync build files to S3
    aws s3 sync frontend/dist/ s3://"$S3_BUCKET" --delete --region "$AWS_REGION"

    # Invalidate CloudFront cache
    CLOUDFRONT_DISTRIBUTION_ID=$(aws cloudfront list-distributions --query "DistributionList.Items[?Comment=='OAI for ${PROJECT_NAME} frontend'].Id" --output text --region "$AWS_REGION")
    if [ ! -z "$CLOUDFRONT_DISTRIBUTION_ID" ]; then
        aws cloudfront create-invalidation --distribution-id "$CLOUDFRONT_DISTRIBUTION_ID" --paths "/*" --region "$AWS_REGION"
    fi

    print_status "Frontend deployed successfully!"
}

# Main deployment function
main() {
    print_status "Starting CityCamp AI deployment to AWS..."

    # Check prerequisites
    check_prerequisites

    # Create ECR repositories
    create_ecr_repositories

    # Build and push Docker images
    build_and_push_images

    # Deploy infrastructure
    deploy_infrastructure

    # Store secrets
    store_secrets

    # Deploy ECS services
    deploy_ecs_services

    # Deploy frontend
    deploy_frontend

    # Wait for service to be stable
    print_status "Waiting for service to stabilize..."
    aws ecs wait services-stable \
        --cluster "${PROJECT_NAME}-cluster" \
        --services "${PROJECT_NAME}-backend" \
        --region "$AWS_REGION"

    print_status "✅ Deployment completed successfully!"

    # Initialize topics in production database
    print_status "Initializing notification topics..."

    # Get the ALB DNS name
    ALB_DNS=$(aws elbv2 describe-load-balancers \
        --names "${PROJECT_NAME}-alb" \
        --query 'LoadBalancers[0].DNSName' \
        --output text \
        --region "$AWS_REGION")

    if [ "$ALB_DNS" != "None" ] && [ -n "$ALB_DNS" ]; then
        # Wait a bit for the service to be ready
        sleep 30

        # Try to initialize topics
        if curl -f -X POST "http://$ALB_DNS/api/v1/subscriptions/admin/initialize-topics" > /dev/null 2>&1; then
            print_status "✅ Notification topics initialized successfully"
        else
            print_warning "⚠️ Could not auto-initialize topics. Run this manually after deployment:"
            echo "curl -X POST http://$ALB_DNS/api/v1/subscriptions/admin/initialize-topics"
        fi
    else
        print_warning "⚠️ Could not get ALB DNS. Initialize topics manually with:"
        echo "curl -X POST https://your-domain.com/api/v1/subscriptions/admin/initialize-topics"
    fi

    print_status "Your application should be available at the CloudFront URL shown above."
}

# Check if environment variables are set
if [ -z "$DATABASE_URL" ] || [ -z "$REDIS_URL" ]; then
    print_error "Required environment variables not set. Please set:"
    print_error "  DATABASE_URL - PostgreSQL connection string"
    print_error "  REDIS_URL - Redis connection string"
    print_error "Optional:"
    print_error "  SECRET_KEY - Application secret key"
    print_error "  OPENAI_API_KEY - OpenAI API key"
    print_error "  TWILIO_ACCOUNT_SID - Twilio account SID"
    print_error "  TWILIO_AUTH_TOKEN - Twilio auth token"
    print_error "  TWILIO_PHONE_NUMBER - Twilio phone number"
    print_error "  SMTP_USERNAME - SMTP username"
    print_error "  SMTP_PASSWORD - SMTP password"
    exit 1
fi

# Run main function
main "$@"
