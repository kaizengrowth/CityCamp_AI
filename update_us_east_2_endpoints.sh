#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Updating SSM parameters with us-east-2 endpoints...${NC}"

# Get the new endpoints from Terraform outputs
cd aws/terraform

echo -e "${YELLOW}Getting Terraform outputs...${NC}"
RDS_ENDPOINT=$(terraform output -raw rds_endpoint)
REDIS_ENDPOINT=$(terraform output -raw redis_endpoint)

echo -e "${GREEN}New endpoints:${NC}"
echo "  RDS: $RDS_ENDPOINT"
echo "  Redis: $REDIS_ENDPOINT"

# Update database URL
echo -e "${YELLOW}Updating database URL...${NC}"
aws ssm put-parameter \
  --region us-east-2 \
  --name "/citycamp-ai/database-url" \
  --value "postgresql://citycamp_user:REDACTED_PASSWORD@$RDS_ENDPOINT/citycamp_db" \
  --type SecureString \
  --overwrite

# Update Redis URL
echo -e "${YELLOW}Updating Redis URL...${NC}"
aws ssm put-parameter \
  --region us-east-2 \
  --name "/citycamp-ai/redis-url" \
  --value "redis://$REDIS_ENDPOINT:6379/0" \
  --type SecureString \
  --overwrite

echo -e "${GREEN}SSM parameters updated successfully!${NC}"
echo -e "${YELLOW}Verifying parameters...${NC}"

# Verify the parameters
aws ssm get-parameter --region us-east-2 --name "/citycamp-ai/database-url" --with-decryption --query "Parameter.Value" --output text
aws ssm get-parameter --region us-east-2 --name "/citycamp-ai/redis-url" --with-decryption --query "Parameter.Value" --output text

echo -e "${GREEN}Parameter update completed!${NC}"
