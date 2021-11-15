variable "AWS_REGION"{
    default = "ap-south-1"
}


variable "AWS_ACCESS_KEY_ID" {
  type = string
}
variable "AWS_SECRET_ACCESS_KEY" {
  type      = string
  sensitive = true
}