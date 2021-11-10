variable "AWS_REGION" {
  default = "ap-south-1"

}

variable "AWS_ACCESS_KEY_ID" {
  type = string
}
variable "AWS_SECRET_ACCESS_KEY" {
  type      = string
  sensitive = true
}

variable "PATH_TO_PUBLIC_KEY" {
  default = "mykey.pub"
}

variable "PATH_TO_PRIVATE_KEY" {
  default = "mykey"
}

variable "additional_tags" {
  default     = { "type" = "challenge1" }
  description = "Additional resource tags"
  type        = map(string)
}

variable "CHALLENGE_REF" {
}
