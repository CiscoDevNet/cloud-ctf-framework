resource "aws_s3_bucket" "ctf-confidential-logs" {
  bucket = "ctf-confidential-logs"
  acl    = "public-read"

  tags = {
    Name        = "ctf-confidential-logs"
  }
}

resource "aws_s3_bucket_public_access_block" "ctf-confidential-logs" {
  bucket = aws_s3_bucket.ctf-confidential-logs.id

  block_public_acls   = false
  block_public_policy = false
  ignore_public_acls = false
  restrict_public_buckets = false
}