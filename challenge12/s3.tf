resource "aws_s3_bucket" "ctf-important-logs" {
  bucket_prefix = "ctf-important-logs-"
  acl    = "private"

  tags = {
    Name        = "ctf-important-logs"
  }
}


output "bucket_name" {
    description = "bucket name"
    value = aws_s3_bucket.ctf-important-logs.id
}