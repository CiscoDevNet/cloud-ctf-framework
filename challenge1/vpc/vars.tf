variable "AWS_REGION"{
    default = "ap-south-1"
    #default = "us-east-1"
    
}

variable "PATH_TO_PUBLIC_KEY" {
  default = "mykey.pub"
}

variable "PATH_TO_PRIVATE_KEY" {
  default = "mykey"
}


variable "images" {
  type = "map"
  default = {
    "ap-south-1" = "ami-041db4a969fe3eb68"
    "us-east-1" = "ami-01cc34ab2709337aa"
    "eu-west-2" = "ami-074771aa49ab046e7"
  }
}

