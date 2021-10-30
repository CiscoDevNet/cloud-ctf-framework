provider "aws" {
  region = var.AWS_REGION
}

terraform {
    backend "s3"{
        bucket="terraform-infra-state-ctf"
        key ="team1-chall1"
        region="ap-south-1"
    }
}