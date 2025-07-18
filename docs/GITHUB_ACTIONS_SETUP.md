# GitHub Actions CI/CD Setup Guide

This guide will help you set up continuous integration and deployment using GitHub Actions with your AWS infrastructure.

## Prerequisites

1. ✅ **AWS Infrastructure Deployed** - Your AWS resources are already set up
2. ✅ **GitHub Repository** - Your code is in a GitHub repository
3. 🔧 **AWS IAM User** - You'll need to create this for GitHub Actions

## Step 1: Create AWS IAM User for GitHub Actions

### 1.1 Create IAM User

```bash
# Create IAM user for GitHub Actions
aws iam create-user --user-name github-actions-citycamp-ai

# Create access key
aws iam create-access-key --user-name github-actions-citycamp-ai
```

### 1.2 Create IAM Policy

Create a policy with the necessary permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecr:GetAuthorizationToken",
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage",
                "ecr:InitiateLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:CompleteLayerUpload",
                "ecr:PutImage"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ecs:UpdateService",
                "ecs:DescribeServices",
                "ecs:RegisterTaskDefinition",
                "ecs:DescribeTaskDefinition"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket",
                "s3:PutObjectAcl"
            ],
            "Resource": [
                "arn:aws:s3:::citycamp-ai-frontend-*",
                "arn:aws:s3:::citycamp-ai-frontend-*/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "cloudfront:CreateInvalidation",
                "cloudfront:GetDistribution",
                "cloudfront:ListDistributions"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "iam:PassRole"
            ],
            "Resource": "arn:aws:iam::*:role/citycamp-ai-ecs-*"
        }
    ]
}
```

### 1.3 Attach Policy to User

```bash
# Save the policy above as github-actions-policy.json, then:
aws iam create-policy --policy-name GitHubActionsCityCampAI --policy-document file://github-actions-policy.json

# Attach policy to user
aws iam attach-user-policy --user-name github-actions-citycamp-ai --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/GitHubActionsCityCampAI
```

## Step 2: Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

### Required Secrets

Add these secrets:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `AWS_ACCESS_KEY_ID` | `AKIA...` | Access key from Step 1.1 |
| `AWS_SECRET_ACCESS_KEY` | `...` | Secret key from Step 1.1 |
| `SONAR_TOKEN` | `...` | SonarCloud token (optional) |

### Getting SonarCloud Token (Optional)

1. Go to [SonarCloud](https://sonarcloud.io/)
2. Sign up with your GitHub account
3. Create a new project for your repository
4. Go to Administration → Security → Generate Token
5. Add the token as `SONAR_TOKEN` secret

## Step 3: Update Workflow Configuration

The workflows are already configured with your specific AWS resources:

- **S3 Bucket**: `citycamp-ai-frontend-ru8nls0c`
- **CloudFront Distribution**: `E18KZSTFG2SA46`
- **ECS Cluster**: `citycamp-ai-cluster`
- **ECS Service**: `citycamp-ai-backend`

If any of these change, update the environment variables in `.github/workflows/deploy.yml`.

## Step 4: Test the Setup

### 4.1 Create a Pull Request

1. Create a new branch:
   ```bash
   git checkout -b test-ci-cd
   ```

2. Make a small change (like updating README.md)

3. Commit and push:
   ```bash
   git add .
   git commit -m "Test CI/CD pipeline"
   git push origin test-ci-cd
   ```

4. Create a pull request on GitHub

This will trigger the **Test and Code Quality** workflow.

### 4.2 Deploy to Production

1. Merge the pull request to `main` branch

This will trigger the **Deploy to AWS** workflow.

## Step 5: Monitor Deployments

### GitHub Actions

- Go to your repository → Actions tab
- Monitor workflow runs and logs
- Check for any failures and debug as needed

### AWS Resources

Monitor your AWS resources:

```bash
# Check ECS service status
aws ecs describe-services --cluster citycamp-ai-cluster --services citycamp-ai-backend

# Check CloudFront distribution
aws cloudfront get-distribution --id E18KZSTFG2SA46

# Check S3 bucket contents
aws s3 ls s3://citycamp-ai-frontend-ru8nls0c
```

## Workflow Features

### ✅ What's Included

- **Automated Testing**: Backend (pytest) and Frontend (Jest)
- **Code Quality**: Linting, type checking, security scanning
- **Build & Deploy**: Docker images to ECR, Frontend to S3
- **Infrastructure**: ECS service updates, CloudFront invalidation
- **Notifications**: Success/failure notifications in workflow logs

### 🔄 Workflow Triggers

- **Pull Requests**: Run tests and code quality checks
- **Push to Main**: Full deployment pipeline
- **Push to Develop**: Tests only (no deployment)

### 📊 Monitoring & Reports

- **Test Coverage**: Uploaded to Codecov
- **Security Scans**: Trivy vulnerability scanner
- **Code Quality**: SonarCloud analysis (if configured)

## Troubleshooting

### Common Issues

1. **AWS Permissions Error**
   - Check IAM user permissions
   - Verify secrets are correctly set

2. **ECR Push Failed**
   - Ensure ECR repositories exist
   - Check ECR permissions in IAM policy

3. **ECS Deployment Failed**
   - Verify ECS cluster and service names
   - Check task definition format

4. **S3 Upload Failed**
   - Verify S3 bucket name and permissions
   - Check bucket policy allows GitHub Actions

### Debug Commands

```bash
# Test AWS credentials locally
aws sts get-caller-identity

# Check ECR repositories
aws ecr describe-repositories --region us-east-1

# Check ECS cluster
aws ecs describe-clusters --clusters citycamp-ai-cluster

# Check S3 bucket
aws s3 ls s3://citycamp-ai-frontend-ru8nls0c
```

## Next Steps

1. **Set up monitoring**: Configure CloudWatch alarms
2. **Add staging environment**: Create separate AWS resources for staging
3. **Database migrations**: Add database migration steps to deployment
4. **Rollback strategy**: Implement automated rollback on deployment failure

## Security Best Practices

- ✅ Use IAM roles with minimal required permissions
- ✅ Store secrets in GitHub Secrets (encrypted)
- ✅ Enable vulnerability scanning in workflows
- ✅ Regularly rotate AWS access keys
- ✅ Monitor AWS CloudTrail for unauthorized access

Your CI/CD pipeline is now ready! 🚀
