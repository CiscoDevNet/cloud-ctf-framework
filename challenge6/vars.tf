variable "AWS_REGION"{
    default = "us-east-1" # change this to different region to verify if the s3 backend error appears
    
}


variable "PATH_TO_PUBLIC_KEY" {
  default = "mykey.pub"
}
