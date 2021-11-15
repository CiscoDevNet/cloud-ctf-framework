data "aws_caller_identity" "current" {}

resource "aws_cloudtrail" "ctf" {
  name                          = "ctf-demo-trail"
  s3_bucket_name                = aws_s3_bucket.ctf.id
  s3_key_prefix                 = "prefix"
  include_global_service_events = false
  is_multi_region_trail         = false
  enable_log_file_validation    = false
}

resource "aws_s3_bucket" "ctf" {
  bucket_prefix = "ctf-demo-trail-"
  force_destroy = true

  tags = {
    Name        = "ctf-demo-trail"
  }
}

resource "aws_s3_bucket_policy" "ctf-bucket-policy" {
  bucket = aws_s3_bucket.ctf.id

  
  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AWSCloudTrailAclCheck",
            "Effect": "Allow",
            "Principal": {
              "Service": "cloudtrail.amazonaws.com"
            },
            "Action": "s3:GetBucketAcl",
            "Resource": "${aws_s3_bucket.ctf.arn}"
        },
        {
            "Sid": "AWSCloudTrailWrite",
            "Effect": "Allow",
            "Principal": {
              "Service": "cloudtrail.amazonaws.com"
            },
            "Action": "s3:PutObject",
            "Resource": "${aws_s3_bucket.ctf.arn}/prefix/AWSLogs/${data.aws_caller_identity.current.account_id}/*",
            "Condition": {
                "StringEquals": {
                    "s3:x-amz-acl": "bucket-owner-full-control"
                }
            }
        }
    ]
})
}



output "bucket_name" {
    description = "bucket name"
    value = aws_s3_bucket.ctf.id
}