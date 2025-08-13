# Cost-effective EC2-based infrastructure for us-east-2

# Data source for the latest Amazon Linux 2 AMI
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Security group for EC2 instance
resource "aws_security_group" "ec2_simple" {
  name_prefix = "${var.project_name}-ec2-simple-"
  vpc_id      = module.vpc.vpc_id

  # HTTP access
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTPS access
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # SSH access removed for security - use AWS Systems Manager Session Manager instead
  # ingress {
  #   from_port   = 22
  #   to_port     = 22
  #   protocol    = "tcp"
  #   cidr_blocks = ["0.0.0.0/0"]  # SECURITY RISK - removed
  # }

  # Backend API port (for ALB health checks)
  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }

  # All outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = var.common_tags
}

# IAM role for EC2 instance
resource "aws_iam_role" "ec2_simple_role" {
  name = "${var.project_name}-ec2-simple-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = var.common_tags
}

# IAM policy for SSM access
resource "aws_iam_role_policy" "ec2_simple_ssm_policy" {
  name = "${var.project_name}-ec2-simple-ssm-policy"
  role = aws_iam_role.ec2_simple_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameters",
          "ssm:GetParameter",
          "ssm:GetParametersByPath"
        ]
        Resource = [
          "arn:aws:ssm:${var.aws_region}:${var.aws_account_id}:parameter/citycamp-ai/*"
        ]
      }
    ]
  })
}

# Attach CloudWatch agent policy
resource "aws_iam_role_policy_attachment" "ec2_simple_cloudwatch" {
  role       = aws_iam_role.ec2_simple_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

# Attach SSM managed instance policy
resource "aws_iam_role_policy_attachment" "ec2_simple_ssm" {
  role       = aws_iam_role.ec2_simple_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# Instance profile
resource "aws_iam_instance_profile" "ec2_simple_profile" {
  name = "${var.project_name}-ec2-simple-profile"
  role = aws_iam_role.ec2_simple_role.name

  tags = var.common_tags
}

# User data script to set up Docker and the application
locals {
  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    aws_region   = var.aws_region
    project_name = var.project_name
  }))
}

# EC2 instance
resource "aws_instance" "simple" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = var.instance_type  # Configurable instance type
  key_name               = var.ec2_key_name  # You'll need to specify this
  vpc_security_group_ids = [aws_security_group.ec2_simple.id]
  subnet_id              = module.vpc.public_subnets[0]
  iam_instance_profile   = aws_iam_instance_profile.ec2_simple_profile.name

  user_data = local.user_data

  # Root volume
  root_block_device {
    volume_type           = "gp3"
    volume_size           = 20
    encrypted             = true
    delete_on_termination = true
  }

  # Additional EBS volume for data persistence
  ebs_block_device {
    device_name           = "/dev/sdf"
    volume_type           = "gp3"
    volume_size           = 20
    encrypted             = true
    delete_on_termination = false
  }

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-simple-instance"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# Elastic IP for the instance
resource "aws_eip" "simple" {
  instance = aws_instance.simple.id
  domain   = "vpc"

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-simple-eip"
  })

  depends_on = [aws_instance.simple]
}

# Update ALB to target the EC2 instance instead of ECS
resource "aws_lb_target_group" "simple" {
  name     = "${var.project_name}-simple-tg"
  port     = 8000
  protocol = "HTTP"
  vpc_id   = module.vpc.vpc_id

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }

  tags = var.common_tags
}

# Target group attachment
resource "aws_lb_target_group_attachment" "simple" {
  target_group_arn = aws_lb_target_group.simple.arn
  target_id        = aws_instance.simple.id
  port             = 8000
}

# Update ALB listener to use the new target group
resource "aws_lb_listener" "simple" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.simple.arn
  }

  tags = var.common_tags
}

# Outputs
output "ec2_public_ip" {
  description = "Public IP of the EC2 instance"
  value       = aws_eip.simple.public_ip
}

output "ec2_instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.simple.id
}
