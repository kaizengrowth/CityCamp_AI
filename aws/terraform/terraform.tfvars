# Copy this file to terraform.tfvars and fill in your values

aws_region     = "us-east-2"
aws_account_id = "538569249671"
project_name   = "citycamp-ai"

# SENSITIVE: Your domain name
domain_name = "tulsai.city"

# SENSITIVE: Git repository URL for application deployment
repository_url = "https://github.com/kaizengrowth/CityCamp_AI.git"

# EC2 configuration
instance_type = "t3.medium" # Options: t3.medium (~$30/mo), t3.large (~$60/mo), m6i.large (~$70/mo)
ec2_instance_type = "t3.medium"
# ec2_key_name = "your-key-pair-name"  # Uncomment and set if you want SSH access

# Optional: Override defaults
# key_pair_name = "your-key-pair-name"
