variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-2"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "citycamp-ai"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones"
  type        = list(string)
  default     = ["us-east-2a", "us-east-2b"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24"]
}

variable "ec2_instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"
}

variable "key_pair_name" {
  description = "Name of the AWS key pair for EC2 access"
  type        = string
  default     = ""
}

variable "domain_name" {
  description = "Primary domain name"
  type        = string
  default     = "example.com"
  sensitive   = true
}

variable "aws_account_id" {
  description = "AWS account ID"
  type        = string
  default     = "123456789012"
  sensitive   = true
}

variable "instance_type" {
  description = "EC2 instance type for the simple deployment"
  type        = string
  default     = "t3.medium"

  validation {
    condition     = contains(["t3.small", "t3.medium", "t3.large", "t3.xlarge", "m5.large", "m5.xlarge", "m6i.large", "m6i.xlarge"], var.instance_type)
    error_message = "Instance type must be one of: t3.small, t3.medium, t3.large, t3.xlarge, m5.large, m5.xlarge, m6i.large, m6i.xlarge."
  }
}

variable "ec2_key_name" {
  description = "EC2 Key Pair name for SSH access"
  type        = string
  default     = null
}

variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    Project     = "CityCamp AI"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}
