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
  bucket        = "ctf-demo-trail"
  force_destroy = true

  policy = <<POLICY
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AWSCloudTrailAclCheck",
            "Effect": "Allow",
            "Principal": {
              "Service": "cloudtrail.amazonaws.com"
            },
            "Action": "s3:GetBucketAcl",
            "Resource": "arn:aws:s3:::ctf-demo-trail"
        },
        {
            "Sid": "AWSCloudTrailWrite",
            "Effect": "Allow",
            "Principal": {
              "Service": "cloudtrail.amazonaws.com"
            },
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::ctf-demo-trail/prefix/AWSLogs/${data.aws_caller_identity.current.account_id}/*",
            "Condition": {
                "StringEquals": {
                    "s3:x-amz-acl": "bucket-owner-full-control"
                }
            }
        }
    ]
}
POLICY
}