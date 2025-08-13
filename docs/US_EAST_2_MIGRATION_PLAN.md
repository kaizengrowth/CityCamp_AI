# Non-Destructive Migration to us-east-2

## Overview
This document outlines the step-by-step process for migrating the CityCamp AI infrastructure from us-east-1 to us-east-2 without service interruption.

## Migration Strategy: Blue-Green Deployment

We'll use a blue-green deployment approach:
- **Blue (Current)**: us-east-1 infrastructure (production)
- **Green (New)**: us-east-2 infrastructure (parallel deployment)

## Prerequisites Checklist

- [ ] Terraform backend for us-east-2 created
- [ ] Database backup completed
- [ ] Redis data export completed
- [ ] DNS TTL reduced to 60 seconds (24 hours before migration)
- [ ] Monitoring setup for both regions

## Phase 1: Infrastructure Preparation

### 1.1 Create us-east-2 Backend
```bash
# Update backend script for us-east-2
./aws/scripts/setup-terraform-backend.sh
```

### 1.2 Deploy Parallel Infrastructure
- Create VPC, subnets, security groups in us-east-2
- Deploy ECS cluster and services
- Set up load balancer and CloudFront (already global)

### 1.3 Verify Infrastructure
- Health checks pass
- All services responding
- Security groups configured correctly

## Phase 2: Data Migration

### 2.1 Database Migration
```bash
# Create RDS snapshot in us-east-1
aws rds create-db-snapshot --db-instance-identifier citycamp-ai-db --db-snapshot-identifier citycamp-migration-$(date +%Y%m%d)

# Copy snapshot to us-east-2
aws rds copy-db-snapshot --source-region us-east-1 --target-region us-east-2 \
  --source-db-snapshot-identifier citycamp-migration-$(date +%Y%m%d) \
  --target-db-snapshot-identifier citycamp-migration-$(date +%Y%m%d)

# Restore in us-east-2
aws rds restore-db-instance-from-db-snapshot --region us-east-2 \
  --db-instance-identifier citycamp-ai-db-us-east-2 \
  --db-snapshot-identifier citycamp-migration-$(date +%Y%m%d)
```

### 2.2 Redis Migration
```bash
# Export Redis data from us-east-1
redis-cli --rdb dump.rdb

# Import to us-east-2 Redis instance
# (Will be done during maintenance window)
```

## Phase 3: Application Deployment

### 3.1 Deploy Application to us-east-2
- Update ECS task definitions with us-east-2 database endpoints
- Deploy latest application version
- Verify all services are healthy

### 3.2 Smoke Testing
- Run automated tests against us-east-2 infrastructure
- Verify database connectivity
- Test all API endpoints
- Validate frontend functionality

## Phase 4: Traffic Migration

### 4.1 DNS Preparation
```bash
# Reduce TTL to 60 seconds (do this 24 hours before)
aws route53 change-resource-record-sets --hosted-zone-id Z00825362FJ8FZMZBHMBR \
  --change-batch '{
    "Changes": [{
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "tulsai.city",
        "Type": "A",
        "TTL": 60,
        "ResourceRecords": [{"Value": "current-ip"}]
      }
    }]
  }'
```

### 4.2 Gradual Traffic Shift
1. **0% → 10%**: Route 10% of traffic to us-east-2
2. **Monitor for 30 minutes**
3. **10% → 50%**: If healthy, increase to 50%
4. **Monitor for 30 minutes**
5. **50% → 100%**: Complete migration

### 4.3 DNS Update
```bash
# Point DNS to us-east-2 load balancer
aws route53 change-resource-record-sets --hosted-zone-id Z00825362FJ8FZMZBHMBR \
  --change-batch '{
    "Changes": [{
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "tulsai.city",
        "Type": "A",
        "AliasTarget": {
          "DNSName": "us-east-2-alb-dns-name",
          "EvaluateTargetHealth": false,
          "HostedZoneId": "Z35SXDOTRQ7X7K"
        }
      }
    }]
  }'
```

## Phase 5: Monitoring and Validation

### 5.1 Health Monitoring
- Monitor application metrics
- Check error rates
- Verify database performance
- Monitor latency improvements

### 5.2 Rollback Plan
If issues arise:
```bash
# Immediate rollback via DNS
aws route53 change-resource-record-sets --hosted-zone-id Z00825362FJ8FZMZBHMBR \
  --change-batch '{
    "Changes": [{
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "tulsai.city",
        "Type": "A",
        "AliasTarget": {
          "DNSName": "us-east-1-alb-dns-name",
          "EvaluateTargetHealth": false,
          "HostedZoneId": "Z35SXDOTRQ7X7K"
        }
      }
    }]
  }'
```

## Phase 6: Cleanup

### 6.1 Verification Period
- Run in parallel for 7 days
- Monitor both regions
- Ensure us-east-2 is stable

### 6.2 Decommission us-east-1
```bash
# After 7 days of stable operation
cd aws/terraform
terraform destroy  # For us-east-1 resources
```

## Cost Considerations

### During Migration (Temporary)
- **Double infrastructure costs** for 7 days
- **Data transfer costs** for migration
- **Estimated additional cost**: ~$200-300 for migration week

### Post-Migration Benefits
- **Reduced latency** to Tulsa, OK
- **Same ongoing costs** as current setup
- **No NAT Gateway costs** (already eliminated)

## Timeline

- **Day -1**: Reduce DNS TTL, create backups
- **Day 0**: Deploy us-east-2 infrastructure (2-4 hours)
- **Day 0**: Migrate data (1-2 hours)
- **Day 0**: Traffic migration (2-4 hours)
- **Day 1-7**: Monitoring period
- **Day 7**: Cleanup us-east-1

## Risk Mitigation

1. **Database Backup**: Multiple snapshots before migration
2. **Rollback Plan**: Immediate DNS rollback capability
3. **Gradual Migration**: Phased traffic shift
4. **Monitoring**: Comprehensive health checks
5. **Testing**: Thorough validation before traffic shift

## Success Criteria

- [ ] All services healthy in us-east-2
- [ ] Database migration successful with zero data loss
- [ ] Application functionality verified
- [ ] Latency improved for Tulsa users
- [ ] No increase in error rates
- [ ] Cost neutral or reduced
