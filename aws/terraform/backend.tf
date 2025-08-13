terraform {
  backend "s3" {
    bucket         = "citycamp-ai-terraform-state-us-east-2"
    key            = "terraform.tfstate"
    region         = "us-east-2"
    encrypt        = true
    dynamodb_table = "citycamp-ai-terraform-locks-us-east-2"
  }
}
