# ☁️ AWS Deployment for CityCamp AI

This directory contains comprehensive AWS deployment tools and configurations for CityCamp AI production infrastructure.

## 🌐 Current Production Status

**✅ Live Application**: https://d1s9nkkr0t3pmn.cloudfront.net
**✅ Backend API**: Operational via CloudFront/ALB routing
**✅ Database**: RDS PostgreSQL with 42+ meetings imported
**✅ Infrastructure**: Full ECS Fargate + CloudFront deployment
**✅ Monitoring**: CloudWatch logs and health checks active

## 🚀 Quick Start

### **Prerequisites**
- ☁️ **AWS CLI** installed and configured (`aws --version`)
- 🐳 **Docker** installed (`docker --version`)
- 🏗️ **Terraform** >= 1.0 (`terraform --version`)
- 📊 **AWS Account** with appropriate permissions
- 🔐 **Domain name** (optional but recommended)

### **⚡ Rapid Deployment**

```bash
# 1. Quick infrastructure check
./scripts/test_production_api.sh

# 2. Fix any production issues
./scripts/fix_production_api.sh

# 3. Full deployment (if needed)
./aws/scripts/deploy.sh
```

## 🔧 Deployment Options

### **Option A: Health Check & Quick Fix** ⭐
```bash
# Check current production status
./scripts/test_production_api.sh

# Auto-fix common production issues
./scripts/fix_production_api.sh

# Status: Most issues resolved in 3-5 minutes
```

### **Option B: Automated Full Deployment**
```bash
# Set required environment variables
export DATABASE_URL="postgresql://citycamp_user:REDACTED_PASSWORD@citycamp-ai-db.c8lywk6yg0um.us-east-1.rds.amazonaws.com:5432/citycamp_db"
export REDIS_URL="redis://citycamp-ai-redis.2gtiq7.0001.use1.cache.amazonaws.com:6379/0"
export SECRET_KEY="$(openssl rand -base64 32)"

# Deploy everything
./aws/scripts/deploy.sh
```

### **Option C: Manual Infrastructure Setup**

1. **Deploy Infrastructure with Terraform**
```bash
cd aws/terraform

# Configure variables
cp terraform.tfvars.example terraform.tfvars
# Edit with your specific values

# Deploy
terraform init
terraform plan
terraform apply
```

2. **Build and Deploy Services**
```bash
# Get AWS account info
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION="us-east-1"

# Build and push Docker images
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

docker build -t $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/citycamp-ai-backend:latest ./backend
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/citycamp-ai-backend:latest

# Deploy ECS service
aws ecs register-task-definition --cli-input-json file://aws/ecs/task-definition-updated.json --region $REGION
aws ecs update-service --cluster citycamp-ai-cluster --service citycamp-ai-service --force-new-deployment
```

## 🏗️ Infrastructure Architecture

### **Current Production Resources**

| Resource | Status | Details |
|----------|--------|---------|
| 🌐 **CloudFront** | ✅ Active | `d1s9nkkr0t3pmn.cloudfront.net` |
| 🏗️ **Application Load Balancer** | ✅ Active | Routes API traffic to ECS |
| 🚀 **ECS Fargate Cluster** | ✅ Running | `citycamp-ai-cluster` |
| 🗃️ **RDS PostgreSQL** | ✅ Active | `citycamp-ai-db.c8lywk6yg0um.us-east-1.rds.amazonaws.com` |
| 💨 **ElastiCache Redis** | ✅ Active | `citycamp-ai-redis.2gtiq7.0001.use1.cache.amazonaws.com` |
| 📦 **S3 Frontend Bucket** | ✅ Active | Static React app hosting |
| 🔐 **Parameter Store** | ✅ Configured | Secrets management |

### **Architecture Diagram**
```
Internet
    │
    ▼
┌─────────────────┐
│   CloudFront    │ ── Caches & Routes requests
│   Distribution  │
└─────────────────┘
    │
    ├──/api/*── ┌─────────────────┐    ┌─────────────────┐
    │           │      ALB        │───▶│   ECS Fargate   │
    │           │  Load Balancer  │    │   (Backend)     │
    │           └─────────────────┘    └─────────────────┘
    │                                           │
    └──/*────── ┌─────────────────┐             │
                │   S3 Bucket     │             ▼
                │  (Frontend)     │    ┌─────────────────┐
                └─────────────────┘    │   PostgreSQL    │
                                       │     (RDS)       │
                                       └─────────────────┘
                                               │
                                       ┌─────────────────┐
                                       │     Redis       │
                                       │ (ElastiCache)   │
                                       └─────────────────┘
```

## 🛠️ Production Troubleshooting

### **🚨 Emergency Response**
```bash
# Step 1: Quick health check
./scripts/test_production_api.sh

# Step 2: Auto-fix most issues
./scripts/fix_production_api.sh

# Step 3: Manual intervention (if needed)
aws ecs describe-services --cluster citycamp-ai-cluster --services citycamp-ai-service
```

### **Common Production Issues**

| Issue | Quick Fix | Command |
|-------|-----------|---------|
| 🔴 **Meeting details not loading** | Cache invalidation | `./scripts/fix_production_api.sh` |
| 🔴 **Backend service unhealthy** | Force deployment | `aws ecs update-service --force-new-deployment` |
| 🔴 **API timeouts** | Check ECS logs | `aws logs tail /ecs/citycamp-ai-backend --follow` |
| 🔴 **Frontend not updating** | Clear CloudFront cache | Included in fix script |

### **Advanced Troubleshooting**

**Check ECS Service Health:**
```bash
aws ecs describe-services --cluster citycamp-ai-cluster --services citycamp-ai-service --query 'services[0].[status,runningCount,desiredCount]'
```

**Monitor Backend Logs:**
```bash
aws logs tail /ecs/citycamp-ai-backend --since 15m --follow
```

**Test Database Connectivity:**
```bash
psql "postgresql://citycamp_user:REDACTED_PASSWORD@citycamp-ai-db.c8lywk6yg0um.us-east-1.rds.amazonaws.com:5432/citycamp_db" -c "SELECT COUNT(*) FROM meetings;"
```

**CloudFront Cache Management:**
```bash
# Get distribution ID
DISTRIBUTION_ID=$(aws cloudfront list-distributions --query 'DistributionList.Items[0].Id' --output text)

# Create invalidation
aws cloudfront create-invalidation --distribution-id $DISTRIBUTION_ID --paths '/api/*' '/*'
```

## 📊 Monitoring & Health Checks

### **Real-Time Monitoring**
- 📈 **CloudWatch Dashboard**: [ECS Metrics](https://console.aws.amazon.com/cloudwatch/)
- 🔍 **Application Logs**: `/ecs/citycamp-ai-backend`
- 💾 **Database Metrics**: RDS Performance Insights
- 🌐 **CloudFront Analytics**: Request patterns and cache performance

### **Health Check Endpoints**
```bash
# Backend health
curl https://d1s9nkkr0t3pmn.cloudfront.net/health

# API functionality
curl https://d1s9nkkr0t3pmn.cloudfront.net/api/v1/meetings/ | head -50

# Database connectivity
# (Automatic via ECS health checks)
```

### **Key Performance Metrics**
| Metric | Target | Current Status |
|--------|--------|----------------|
| 📈 **API Response Time** | < 500ms | ✅ Achieving |
| 🔄 **Uptime** | > 99% | ✅ Achieving |
| 💾 **Database Connections** | < 80% | ✅ Healthy |
| 🌐 **Cache Hit Ratio** | > 80% | ✅ Optimized |

## 💰 Cost Analysis

### **Current Monthly Costs (us-east-1)**
| Service | Instance Type | Est. Monthly Cost |
|---------|---------------|-------------------|
| 🗃️ **RDS PostgreSQL** | db.t3.micro | $15-20 |
| 💨 **ElastiCache Redis** | cache.t3.micro | $15-20 |
| 🚀 **ECS Fargate** | 0.25 vCPU, 0.5GB | $10-15 |
| 📦 **S3 + CloudFront** | Static hosting | $5-10 |
| 🏗️ **Application Load Balancer** | Standard | $20-25 |
| 🌐 **Data Transfer** | Typical usage | $5-15 |
| **📊 Total Estimate** | | **$70-105/month** |

### **Cost Optimization Opportunities**
- 💡 **Reserved Instances**: 30-50% savings on RDS/ElastiCache
- 💡 **Spot Instances**: Consider for non-critical workloads
- 💡 **CloudFront Optimization**: Fine-tune cache policies
- 💡 **Auto Scaling**: Scale down during low traffic periods

## 🔐 Security & Compliance

### **Security Features Implemented**
- 🛡️ **VPC Isolation**: All resources in private subnets
- 🔐 **Secrets Management**: AWS Parameter Store integration
- 🔑 **IAM Roles**: Minimal permissions principle
- 🌐 **HTTPS Only**: All traffic encrypted in transit
- 📊 **Database Encryption**: At rest and in transit
- 🔍 **Security Groups**: Restrictive network access

### **Security Best Practices**
```bash
# Rotate secrets regularly
aws ssm put-parameter --name "/citycamp-ai/secret-key" --value "$(openssl rand -base64 32)" --type "SecureString" --overwrite

# Monitor security events
aws logs filter-log-events --log-group-name /ecs/citycamp-ai-backend --filter-pattern "ERROR"

# Review IAM permissions
aws iam get-role --role-name citycamp-ai-ecs-task-role
```

## 🚀 Scaling & Performance

### **Auto Scaling Configuration**
```bash
# ECS Service Auto Scaling
aws application-autoscaling register-scalable-target \
    --service-namespace ecs \
    --resource-id service/citycamp-ai-cluster/citycamp-ai-service \
    --scalable-dimension ecs:service:DesiredCount \
    --min-capacity 1 \
    --max-capacity 5

# CPU-based scaling policy
aws application-autoscaling put-scaling-policy \
    --policy-name cpu-scaling \
    --service-namespace ecs \
    --resource-id service/citycamp-ai-cluster/citycamp-ai-service \
    --scalable-dimension ecs:service:DesiredCount \
    --policy-type TargetTrackingScaling
```

### **Database Scaling Options**
- 📈 **Vertical Scaling**: Upgrade instance type
- 🔄 **Read Replicas**: For read-heavy workloads
- 🚀 **Aurora Migration**: For advanced features
- 💾 **Storage Auto Scaling**: Enabled (20GB → 100GB)

## 📦 Backup & Recovery

### **Automated Backup Status**
- ✅ **RDS Backups**: 7-day retention, automated snapshots
- ✅ **Application State**: ECS task definitions versioned
- ✅ **Frontend Assets**: S3 versioning enabled
- ✅ **Configuration**: Terraform state in S3 backend

### **Disaster Recovery Procedures**
```bash
# 1. Database Recovery
aws rds restore-db-instance-from-db-snapshot \
    --db-instance-identifier citycamp-ai-db-recovered \
    --db-snapshot-identifier citycamp-ai-db-snapshot-YYYY-MM-DD

# 2. ECS Service Recovery
aws ecs update-service --cluster citycamp-ai-cluster --service citycamp-ai-service --force-new-deployment

# 3. Frontend Recovery
aws s3 sync s3://backup-bucket/frontend/ s3://citycamp-ai-frontend-xxxxx/
```

## 🔄 Continuous Integration & Deployment

### **Current CI/CD Status**
- ✅ **GitHub Actions**: Automated testing on PRs
- ✅ **Production Deployment**: Manual trigger via scripts
- ✅ **Health Monitoring**: Automated checks post-deployment
- ✅ **Rollback Capability**: ECS service versioning

### **Deployment Pipeline**
```bash
# 1. Build and Test (Automated)
# GitHub Actions runs tests on every PR

# 2. Deploy (Manual/Automated)
./aws/scripts/deploy.sh

# 3. Health Check (Automated)
./scripts/test_production_api.sh

# 4. Fix Issues (Semi-automated)
./scripts/fix_production_api.sh
```

## 📞 Support & Maintenance

### **Emergency Contacts**
- 🚨 **Production Issues**: Run `./scripts/fix_production_api.sh`
- 🔍 **Debugging**: Use `./scripts/test_production_api.sh`
- 📊 **Monitoring**: [CloudWatch Console](https://console.aws.amazon.com/cloudwatch/)
- 💬 **Community**: [GitHub Issues](https://github.com/kaizengrowth/CityCamp_AI/issues)

### **Maintenance Schedule**
- 📅 **Weekly**: Security updates and dependency checks
- 📅 **Monthly**: Performance review and cost optimization
- 📅 **Quarterly**: Infrastructure review and capacity planning

### **Quick Reference Commands**
```bash
# Service status
aws ecs describe-services --cluster citycamp-ai-cluster --services citycamp-ai-service

# Application logs
aws logs tail /ecs/citycamp-ai-backend --follow

# Database status
aws rds describe-db-instances --db-instance-identifier citycamp-ai-db

# CloudFront distribution
aws cloudfront list-distributions --query 'DistributionList.Items[*].[Id,DomainName,Status]'
```

## 🔮 Future Improvements

### **Planned Enhancements**
- 🔄 **Auto Scaling**: CPU/memory-based scaling policies
- 📱 **Multi-Region**: Disaster recovery in us-west-2
- 🛡️ **WAF Integration**: Advanced security filtering
- 📊 **Enhanced Monitoring**: Custom metrics and dashboards
- 🚀 **CI/CD Pipeline**: Fully automated deployments

### **Performance Optimizations**
- ⚡ **Redis Caching**: Extended cache policies
- 🗃️ **Database Optimization**: Query performance tuning
- 🌐 **CDN Enhancement**: Edge location optimization
- 💾 **Storage Efficiency**: S3 lifecycle policies

---

## 📚 Additional Resources

- 📖 **[Main README](../README.md)** - Project overview
- 🧪 **[Testing Guide](../tests/README.md)** - Testing procedures
- 🔧 **[Troubleshooting](../docs/TROUBLESHOOTING.md)** - Issue resolution
- 🚀 **[Quick Start](../docs/QUICKSTART.md)** - Local development

---

**Need immediate help?** Run `./scripts/test_production_api.sh` followed by `./scripts/fix_production_api.sh` to diagnose and resolve most production issues automatically! 🚀
