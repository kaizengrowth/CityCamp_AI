# Copy this file to terraform.tfvars and fill in your values

aws_region     = "us-east-2"
aws_account_id = "538569249671"
project_name   = "citycamp-ai"
instance_type  = "t3.medium"  # Options: t3.medium (~$30/mo), t3.large (~$60/mo), m6i.large (~$70/mo)
# ec2_key_name = "your-key-pair-name"  # Uncomment and set if you want SSH access

# Database configuration
db_password = "your-secure-database-password"

# Optional: Override defaults
# db_instance_class = "db.t3.small"
# redis_node_type = "cache.t3.small" db_password = "REDACTED_PASSWORD"
