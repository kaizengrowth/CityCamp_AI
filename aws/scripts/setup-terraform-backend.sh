#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BUCKET_NAME="citycamp-ai-terraform-state"
DYNAMODB_TABLE="citycamp-ai-terraform-locks"
AWS_REGION="us-east-1"

echo -e "${YELLOW}Setting up Terraform backend resources...${NC}"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}AWS CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}AWS credentials not configured. Please run 'aws configure' first.${NC}"
    exit 1
fi

echo -e "${YELLOW}Creating S3 bucket for Terraform state...${NC}"

# Create S3 bucket
if ! aws s3 ls "s3://${BUCKET_NAME}" &>/dev/null; then
    aws s3 mb "s3://${BUCKET_NAME}" --region "${AWS_REGION}"
    echo -e "${GREEN}S3 bucket '${BUCKET_NAME}' created successfully.${NC}"
else
    echo -e "${YELLOW}S3 bucket '${BUCKET_NAME}' already exists.${NC}"
fi

# Enable versioning on the bucket
aws s3api put-bucket-versioning \
    --bucket "${BUCKET_NAME}" \
    --versioning-configuration Status=Enabled

# Enable server-side encryption
aws s3api put-bucket-encryption \
    --bucket "${BUCKET_NAME}" \
    --server-side-encryption-configuration '{
        "Rules": [
            {
                "ApplyServerSideEncryptionByDefault": {
                    "SSEAlgorithm": "AES256"
                }
            }
        ]
    }'

# Block public access
aws s3api put-public-access-block \
    --bucket "${BUCKET_NAME}" \
    --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

echo -e "${GREEN}S3 bucket configured with versioning, encryption, and public access blocked.${NC}"

echo -e "${YELLOW}Creating DynamoDB table for Terraform state locking...${NC}"

# Create DynamoDB table
if aws dynamodb describe-table --table-name "${DYNAMODB_TABLE}" --region "${AWS_REGION}" &> /dev/null; then
    echo -e "${YELLOW}DynamoDB table '${DYNAMODB_TABLE}' already exists.${NC}"
else
    aws dynamodb create-table \
        --table-name "${DYNAMODB_TABLE}" \
        --attribute-definitions AttributeName=LockID,AttributeType=S \
        --key-schema AttributeName=LockID,KeyType=HASH \
        --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1 \
        --region "${AWS_REGION}"

    echo -e "${YELLOW}Waiting for DynamoDB table to be created...${NC}"
    aws dynamodb wait table-exists --table-name "${DYNAMODB_TABLE}" --region "${AWS_REGION}"
    echo -e "${GREEN}DynamoDB table '${DYNAMODB_TABLE}' created successfully.${NC}"
fi

echo -e "${GREEN}Terraform backend setup completed!${NC}"
echo -e "${YELLOW}Resources created:${NC}"
echo -e "  - S3 Bucket: ${BUCKET_NAME}"
echo -e "  - DynamoDB Table: ${DYNAMODB_TABLE}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Navigate to aws/terraform directory"
echo -e "2. Run 'terraform init' to initialize the backend"
echo -e "3. Your Terraform state will now be stored remotely and locked during operations"
