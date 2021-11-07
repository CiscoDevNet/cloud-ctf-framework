provider "aws" {
  region = var.AWS_REGION
}

terraform {
    backend "s3"{
        bucket="terraform-infra-state-ctf"
        key ="home/terraform.tfstate"
        region="ap-south-1"
    }
}