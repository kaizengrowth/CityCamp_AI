# AWS Deployment Guide for CityCamp AI

## Overview
This guide provides multiple deployment options for the CityCamp AI application on AWS, from simple to production-ready setups.

## Deployment Options

### Option 1: Simple ECS Deployment (Recommended for MVP)
- **Frontend**: S3 + CloudFront
- **Backend**: ECS Fargate
- **Database**: RDS PostgreSQL
- **Cache**: ElastiCache Redis
- **Load Balancer**: Application Load Balancer

### Option 2: Production ECS Deployment
- **Frontend**: S3 + CloudFront + Route 53
- **Backend**: ECS Fargate with Auto Scaling
- **Database**: RDS PostgreSQL Multi-AZ
- **Cache**: ElastiCache Redis Cluster
- **Load Balancer**: Application Load Balancer
- **Monitoring**: CloudWatch + X-Ray
- **CI/CD**: CodePipeline + CodeBuild

### Option 3: Serverless Deployment
- **Frontend**: S3 + CloudFront
- **Backend**: Lambda + API Gateway
- **Database**: RDS PostgreSQL
- **Cache**: ElastiCache Redis

## Prerequisites

1. **AWS CLI installed and configured**
2. **Docker installed**
3. **AWS account with appropriate permissions**
4. **Domain name (optional but recommended)**

## Required AWS Services

### Core Services
- **ECS (Elastic Container Service)** - Container orchestration
- **RDS (Relational Database Service)** - PostgreSQL database
- **ElastiCache** - Redis for caching and Celery
- **S3** - Static file storage for frontend
- **CloudFront** - CDN for frontend
- **Application Load Balancer** - Traffic distribution
- **IAM** - Security and permissions

### Optional Services
- **Route 53** - DNS management
- **Certificate Manager** - SSL certificates
- **CloudWatch** - Monitoring and logging
- **X-Ray** - Distributed tracing
- **CodePipeline** - CI/CD pipeline

## Environment Variables

### Production Environment Variables
```bash
# Database
DATABASE_URL=postgresql://username:password@your-rds-endpoint:5432/citycamp_db
DATABASE_HOST=your-rds-endpoint
DATABASE_PORT=5432
DATABASE_NAME=citycamp_db
DATABASE_USER=your_db_user
DATABASE_PASSWORD=your_secure_password

# Redis
REDIS_URL=redis://your-elasticache-endpoint:6379/0

# Security
SECRET_KEY=your-super-secure-secret-key
ENVIRONMENT=production
DEBUG=False

# AWS
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
AWS_S3_BUCKET=your-s3-bucket-name

# External APIs
OPENAI_API_KEY=your-openai-key
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=your-twilio-number

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email
SMTP_PASSWORD=your-app-password

# CORS
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

## Deployment Steps

### Step 1: Prepare Infrastructure
1. Create VPC with public and private subnets
2. Set up RDS PostgreSQL instance
3. Set up ElastiCache Redis cluster
4. Create S3 bucket for frontend
5. Set up CloudFront distribution
6. Create ECS cluster
7. Set up Application Load Balancer

### Step 2: Build and Push Docker Images
1. Build production Docker images
2. Push to Amazon ECR
3. Create ECS task definitions

### Step 3: Deploy Backend
1. Create ECS service for backend
2. Configure environment variables
3. Set up health checks
4. Configure auto scaling

### Step 4: Deploy Frontend
1. Build production frontend
2. Upload to S3
3. Configure CloudFront
4. Set up custom domain (optional)

### Step 5: Configure Monitoring
1. Set up CloudWatch alarms
2. Configure logging
3. Set up X-Ray tracing (optional)

## Cost Estimation

### Monthly Costs (us-east-1)
- **RDS PostgreSQL (db.t3.micro)**: ~$15-20
- **ElastiCache Redis (cache.t3.micro)**: ~$15-20
- **ECS Fargate (0.25 vCPU, 0.5GB RAM)**: ~$10-15
- **S3 + CloudFront**: ~$5-10
- **Application Load Balancer**: ~$20-25
- **Data Transfer**: ~$5-15
- **Total Estimated**: ~$70-105/month

## Security Considerations

1. **Use IAM roles instead of access keys**
2. **Enable VPC for all resources**
3. **Use security groups to restrict access**
4. **Enable encryption at rest and in transit**
5. **Regular security updates**
6. **Monitor with CloudTrail**

## Monitoring and Maintenance

1. **Set up CloudWatch dashboards**
2. **Configure log aggregation**
3. **Set up alerting for critical metrics**
4. **Regular backup verification**
5. **Performance monitoring**
6. **Cost optimization**

## Next Steps

1. Choose your deployment option
2. Set up AWS infrastructure
3. Configure environment variables
4. Deploy application
5. Set up monitoring
6. Configure custom domain
7. Set up CI/CD pipeline

## Support

For deployment issues:
1. Check CloudWatch logs
2. Verify security group configurations
3. Test connectivity between services
4. Review ECS task definition
5. Check environment variables
