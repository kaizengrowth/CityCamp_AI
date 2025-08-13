# Terraform CI/CD Setup Guide

This guide explains how to set up and use Terraform in the GitHub Actions CI/CD pipeline for the CityCamp AI project.

## Overview

The CI/CD pipeline now includes Terraform automation that:
- **On Pull Requests**: Runs `terraform plan` and comments the plan output on the PR
- **On Main Branch Push**: Runs `terraform apply` to deploy infrastructure changes
- Uses remote state management with S3 backend and DynamoDB locking

## Setup Requirements

### 1. GitHub Secrets

The following secrets must be configured in your GitHub repository settings:

- `AWS_ACCESS_KEY_ID`: AWS access key for Terraform operations
- `AWS_SECRET_ACCESS_KEY`: AWS secret key for Terraform operations

**Note**: These should be the same AWS credentials already used for deployment.

### 2. Terraform Backend Setup

Before the first run, you need to set up the Terraform backend resources:

```bash
# Run the setup script
./aws/scripts/setup-terraform-backend.sh
```

This script creates:
- S3 bucket: `citycamp-ai-terraform-state` (with versioning and encryption)
- DynamoDB table: `citycamp-ai-terraform-locks` (for state locking)

### 3. Initialize Terraform Backend

After running the setup script, initialize Terraform with the remote backend:

```bash
cd aws/terraform
terraform init
```

## Workflow Behavior

### Pull Request Workflow

When you create a PR that affects Terraform files:

1. **Terraform Format Check**: Ensures code is properly formatted
2. **Terraform Init**: Initializes the working directory
3. **Terraform Validate**: Validates the configuration syntax
4. **Terraform Plan**: Creates an execution plan
5. **Comment on PR**: Posts the plan output as a comment on the PR

### Main Branch Deployment

When changes are merged to main:

1. All the same validation steps as PR workflow
2. **Terraform Apply**: Applies the planned changes automatically
3. **Build and Deploy**: Application deployment proceeds after infrastructure changes

## File Structure

```
aws/
├── terraform/
│   ├── main.tf              # Main Terraform configuration
│   ├── variables.tf         # Variable definitions
│   ├── backend.tf           # Backend configuration (S3 + DynamoDB)
│   ├── terraform.tfvars     # Variable values
│   └── terraform.tfvars.example
└── scripts/
    └── setup-terraform-backend.sh  # Backend setup script
```

## Important Notes

### State Management
- Terraform state is stored remotely in S3
- State is automatically locked during operations using DynamoDB
- Multiple team members can safely work with the same state

### Security
- State files are encrypted at rest in S3
- DynamoDB table uses minimal provisioned capacity (1 read/write unit)
- S3 bucket has public access blocked

### Workflow Triggers
The deployment workflow triggers on:
- Push to main branch
- Pull requests to main branch (for plan-only operations)
- Changes to specific paths:
  - `aws/terraform/**`
  - `.github/workflows/deploy.yml`
  - `backend/**`
  - `frontend/**`

## Troubleshooting

### Backend Initialization Issues
If you encounter backend initialization errors:

1. Ensure the S3 bucket and DynamoDB table exist
2. Check AWS credentials have proper permissions
3. Run the backend setup script again if needed

### Plan/Apply Failures
- Check AWS credentials are valid and have necessary permissions
- Ensure terraform.tfvars contains all required variables
- Review the error output in GitHub Actions logs

### State Lock Issues
If state is locked from a previous failed run:
```bash
# Force unlock (use with caution)
terraform force-unlock LOCK_ID
```

## Manual Operations

For manual Terraform operations outside of CI/CD:

```bash
cd aws/terraform

# Plan changes
terraform plan

# Apply changes
terraform apply

# Check current state
terraform show

# Import existing resources
terraform import aws_instance.example i-1234567890abcdef0
```

## Best Practices

1. **Always review plan output** before merging PRs
2. **Test infrastructure changes** in a separate environment first
3. **Keep terraform.tfvars** in sync with your actual configuration
4. **Use semantic versioning** for infrastructure changes in commit messages
5. **Monitor costs** after applying changes that create new resources

## Recent Changes

- ✅ Disabled NAT Gateway to reduce costs
- ✅ Removed VPC endpoints to use public AWS endpoints
- ✅ ECS tasks now use public subnets with public IP assignment
- ✅ All AWS service calls now go through public internet
