variable "AWS_REGION"{
    default = "us-east-1"
}


variable "PATH_TO_PUBLIC_KEY" {
  default = "mykey.pub"
}



variable "AWS_ACCESS_KEY_ID" {
  type = string
}
variable "AWS_SECRET_ACCESS_KEY" {
  type      = string
  sensitive = true
}

variable "availability_zone" {
  type = map(string)
  default = {
    "ap-south-1" = "ap-south-1a"
    "us-east-1" = "us-east-1a"
    "eu-west-2" = "eu-west-2a"
  }
}


variable "images" {
  type = map(string)
  default = {
    "ap-south-1" = "ami-041db4a969fe3eb68"
    "us-east-1" = "ami-01cc34ab2709337aa"
    "eu-west-2" = "ami-074771aa49ab046e7"
  }
}