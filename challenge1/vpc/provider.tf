provider "aws" {
  region = var.AWS_REGION
}

/*
  terraform {
  backend "s3" {
    bucket = "terraform-infra-state-ctf"
    key    = "home/terraform.tfstate"
    region = "ap-south-1"
  }
}
*/ This is the s3 bucket which stores the terraform state on te aws console. This would not be required for the challege deployment stage
