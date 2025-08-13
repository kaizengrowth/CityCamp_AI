terraform {
  backend "s3" {
    bucket         = "citycamp-ai-terraform-state"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "citycamp-ai-terraform-locks"
  }
}
