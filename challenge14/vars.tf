variable "AWS_REGION"{
    default = "ap-south-1"
    #default = "us-east-1"
  
    
}



variable "username" {
  type = "list"
  default = ["dev","prod"]
  
  }