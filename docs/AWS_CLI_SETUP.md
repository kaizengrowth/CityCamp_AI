# AWS CLI Installation Guide

This guide helps you install the AWS CLI properly without adding installer files to your repository.

## 🚨 Important Note

**Never commit installer packages** (like `AWSCLIV2.pkg`) to your Git repository! They are:
- ❌ Large binary files (38MB+)
- ❌ Platform-specific
- ❌ Easily downloadable from AWS
- ❌ Not source code

## Installation Methods

### macOS

#### Option 1: Download and Install (Recommended)
```bash
# Download the installer
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"

# Install it
sudo installer -pkg AWSCLIV2.pkg -target /

# Clean up (important!)
rm AWSCLIV2.pkg
```

#### Option 2: Homebrew
```bash
brew install awscli
```

### Linux

#### Amazon Linux 2/CentOS/RHEL
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
rm -rf awscliv2.zip aws/
```

#### Ubuntu/Debian
```bash
# Via apt
sudo apt update
sudo apt install awscli

# Or latest version
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
rm -rf awscliv2.zip aws/
```

### Windows

#### Option 1: MSI Installer
1. Download: https://awscli.amazonaws.com/AWSCLIV2.msi
2. Run the installer
3. Delete the downloaded MSI file

#### Option 2: PowerShell
```powershell
# Using winget
winget install Amazon.AWSCLI

# Or using chocolatey
choco install awscli
```

## Configuration

After installation, configure your AWS credentials:

```bash
# Configure AWS CLI
aws configure

# You'll be prompted for:
# AWS Access Key ID: [Your access key]
# AWS Secret Access Key: [Your secret key]
# Default region name: us-east-1
# Default output format: json
```

### Alternative: Environment Variables

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

### Alternative: AWS Profiles

```bash
# Create named profiles
aws configure --profile production
aws configure --profile development

# Use specific profile
aws s3 ls --profile production
```

## Verification

Test your installation:

```bash
# Check version
aws --version

# Test credentials
aws sts get-caller-identity

# List S3 buckets (if you have any)
aws s3 ls
```

## For CityCamp AI Project

Once AWS CLI is installed and configured, you can:

1. **Deploy infrastructure**:
   ```bash
   cd aws/terraform
   terraform init
   terraform apply
   ```

2. **Run deployment scripts**:
   ```bash
   ./aws/scripts/deploy.sh
   ```

3. **Use GitHub Actions**:
   - Add `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` to GitHub Secrets
   - Workflows will use these for automated deployment

## Security Best Practices

- ✅ **Use IAM roles** when possible (EC2, Lambda, etc.)
- ✅ **Rotate access keys** regularly
- ✅ **Use least privilege** permissions
- ✅ **Never commit credentials** to Git
- ✅ **Use AWS profiles** for different environments
- ✅ **Enable MFA** on your AWS account

## Troubleshooting

### "aws: command not found"
- **macOS**: Add `/usr/local/bin` to your PATH
- **Linux**: Run `sudo ./aws/install` again
- **Windows**: Restart your terminal/PowerShell

### "Unable to locate credentials"
```bash
# Check configuration
aws configure list

# Reconfigure
aws configure
```

### "Access Denied" errors
- Check your IAM permissions
- Verify you're using the correct AWS account
- Ensure your access key is active

---

**Remember**: Never commit installer files like `AWSCLIV2.pkg` to your repository!
