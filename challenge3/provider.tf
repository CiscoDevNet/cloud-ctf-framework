provider "aws" {
  access_key = var.AWS_ACCESS_KEY_ID
  secret_key = var.AWS_SECRET_ACCESS_KEY
  region     = var.AWS_REGION
}



terraform {
   /* backend "s3"{
        bucket="terraform-infra-state-ctf"
        key ="team1-chall1"
        region="ap-south-1"
    }*/
    
    backend "local" {
        path = "/var/data/terraform/terraform.tfstate"
    }
}