variable "AWS_ACCESS_KEY_ID" {
  type = string
}
variable "AWS_SECRET_ACCESS_KEY" {
  type      = string
  sensitive = true
}
variable "AWS_REGION" {
  type = string
}
variable "vpc_cidr" { default = "10.0.0.0/16" }
variable "subnet_one_cidr" { default = "10.0.1.0/24" }
variable "subnet_two_cidr" { default = ["10.0.2.0/24", "10.0.3.0/24"] }
variable "route_table_cidr" { default = "0.0.0.0/0" }
variable "host" { default = "aws_instance.my_web_instance.public_dns" }
variable "web_ports" { default = ["22", "80", "443", "3306"] }
variable "db_ports" { default = ["22", "3306"] }
variable "images" {
  type = map(string)
  default = {
    "us-east-1"      = "ami-04ad2567c9e3d7893"
    "ap-south-1"     = "ami-0f1fb91a596abf28d"
    "eu-west-2"      = "ami-0fc15d50d39e4503c"
  }
}