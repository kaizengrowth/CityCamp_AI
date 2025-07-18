# AWS Deployment for CityCamp AI

This directory contains all the necessary files and scripts to deploy CityCamp AI to AWS.

## Quick Start

### Prerequisites

1. **AWS CLI** installed and configured
2. **Docker** installed
3. **Terraform** installed
4. **AWS account** with appropriate permissions
5. **Domain name** (optional but recommended)

### 1. Setup Production Configuration

```bash
# Make scripts executable
chmod +x aws/scripts/*.sh

# Setup production Dockerfiles and configuration
./aws/scripts/setup-production-dockerfiles.sh
```

### 2. Configure Environment Variables

```bash
# Copy the production environment template
cp .env.production.template .env.production

# Edit the file with your actual values
nano .env.production
```

Required environment variables:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `SECRET_KEY` - Application secret key

### 3. Deploy to AWS

#### Option A: Automated Deployment (Recommended)

```bash
# Set required environment variables
export DATABASE_URL="postgresql://username:password@your-rds-endpoint:5432/citycamp_db"
export REDIS_URL="redis://your-elasticache-endpoint:6379/0"
export SECRET_KEY="your-secure-secret-key"

# Run the automated deployment script
./aws/scripts/deploy.sh
```

#### Option B: Manual Deployment

1. **Deploy Infrastructure with Terraform**

```bash
cd aws/terraform

# Copy and configure variables
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values

# Initialize and deploy
terraform init
terraform plan
terraform apply
```

2. **Build and Push Docker Images**

```bash
# Get your AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION="us-east-1"

# Login to ECR
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Build and push backend
docker build -t $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/citycamp-ai-backend:latest ./backend
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/citycamp-ai-backend:latest

# Build and push frontend
docker build -t $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/citycamp-ai-frontend:latest ./frontend
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/citycamp-ai-frontend:latest
```

3. **Deploy ECS Services**

```bash
# Update task definition with your account ID and region
sed "s/ACCOUNT_ID/$ACCOUNT_ID/g; s/REGION/$REGION/g" aws/ecs/task-definition.json > aws/ecs/task-definition-updated.json

# Register task definition
aws ecs register-task-definition --cli-input-json file://aws/ecs/task-definition-updated.json --region $REGION

# Create ECS service
aws ecs create-service \
    --cluster citycamp-ai-cluster \
    --service-name citycamp-ai-backend \
    --task-definition citycamp-ai-backend \
    --desired-count 1 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-12345678,subnet-87654321],securityGroups=[sg-12345678],assignPublicIp=DISABLED}" \
    --region $REGION
```

4. **Deploy Frontend to S3**

```bash
# Build frontend
cd frontend
npm run build

# Sync to S3 (replace with your bucket name)
aws s3 sync dist/ s3://citycamp-ai-frontend-xxxxx --delete --region $REGION

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id YOUR_DISTRIBUTION_ID --paths "/*" --region $REGION
```

## Infrastructure Overview

The deployment creates the following AWS resources:

### Core Infrastructure
- **VPC** with public and private subnets
- **RDS PostgreSQL** database
- **ElastiCache Redis** cluster
- **ECS Fargate** cluster
- **Application Load Balancer**
- **S3 bucket** for frontend
- **CloudFront** distribution

### Security
- **Security Groups** for each service
- **IAM roles** for ECS tasks
- **Parameter Store** for secrets

### Monitoring
- **CloudWatch** logs
- **ECS Container Insights**

## Cost Estimation

Monthly costs (us-east-1):
- RDS PostgreSQL (db.t3.micro): ~$15-20
- ElastiCache Redis (cache.t3.micro): ~$15-20
- ECS Fargate (0.25 vCPU, 0.5GB RAM): ~$10-15
- S3 + CloudFront: ~$5-10
- Application Load Balancer: ~$20-25
- Data Transfer: ~$5-15
- **Total**: ~$70-105/month

## Security Best Practices

1. **Use IAM roles** instead of access keys
2. **Enable VPC** for all resources
3. **Use security groups** to restrict access
4. **Enable encryption** at rest and in transit
5. **Store secrets** in Parameter Store
6. **Monitor** with CloudTrail

## Monitoring and Maintenance

### CloudWatch Dashboards
Create dashboards for:
- ECS service metrics
- RDS performance
- Application logs
- Error rates

### Alerts
Set up CloudWatch alarms for:
- High CPU/memory usage
- Database connections
- Error rates
- Response times

### Logs
Monitor logs in CloudWatch:
- Application logs
- Access logs
- Error logs

## Troubleshooting

### Common Issues

1. **ECS tasks not starting**
   - Check task definition
   - Verify IAM roles
   - Check security groups

2. **Database connection issues**
   - Verify security groups
   - Check connection string
   - Test connectivity

3. **Frontend not loading**
   - Check S3 bucket permissions
   - Verify CloudFront distribution
   - Check CORS settings

### Useful Commands

```bash
# Check ECS service status
aws ecs describe-services --cluster citycamp-ai-cluster --services citycamp-ai-backend

# View CloudWatch logs
aws logs tail /ecs/citycamp-ai-backend --follow

# Check RDS status
aws rds describe-db-instances --db-instance-identifier citycamp-ai-db

# Test database connectivity
psql "postgresql://username:password@your-rds-endpoint:5432/citycamp_db"
```

## Scaling

### Auto Scaling
Configure auto scaling for ECS services:
- CPU utilization > 70%
- Memory utilization > 80%
- Target tracking scaling

### Database Scaling
- Enable Multi-AZ for high availability
- Use read replicas for read-heavy workloads
- Consider Aurora for better performance

## Backup and Recovery

### Database Backups
- Automated backups enabled
- Point-in-time recovery
- Cross-region backup copies

### Application Data
- S3 versioning enabled
- Cross-region replication
- Regular snapshots

## Updates and Maintenance

### Application Updates
1. Build new Docker images
2. Update ECS task definition
3. Deploy new version
4. Monitor health checks

### Infrastructure Updates
1. Update Terraform configuration
2. Run `terraform plan`
3. Apply changes
4. Verify functionality

## Support

For deployment issues:
1. Check CloudWatch logs
2. Verify security group configurations
3. Test connectivity between services
4. Review ECS task definition
5. Check environment variables

## Next Steps

1. Set up custom domain with Route 53
2. Configure SSL certificates
3. Set up CI/CD pipeline
4. Implement monitoring and alerting
5. Configure backup strategies 