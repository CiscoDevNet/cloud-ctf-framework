resource "aws_s3_bucket" "ctf-important-logs" {
  bucket = "ctf-important-logs"
  acl    = "private"

  tags = {
    Name        = "ctf-important-logs"
  }
}