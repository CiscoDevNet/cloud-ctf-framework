locals {
    s3_origin_id = "S3-content-bucket"
}

#S3 bucket
resource "aws_s3_bucket" "ctf-content"{
    bucket = "ctf-content"
    acl = "private"
    versioning{
        enabled = true
    }
    server_side_encryption_configuration{
        rule {
            apply_server_side_encryption_by_default{
                sse_algorithm = "AES256"
            }
        }
    }
    tags = {
        Name = "ctf_content"

    }
}

#Bucket policy
resource "aws_s3_bucket_public_access_block" "testacl"{
    bucket = aws_s3_bucket.ctf-content.id
    block_public_acls = true
    block_public_policy = true
    restrict_public_buckets = true
    ignore_public_acls  = true
}


#S3 bucket files
resource "aws_s3_bucket_object" "files" {
    bucket = aws_s3_bucket.ctf-content.id
    key = "data/webex.jpeg"
    source = "/Users/bhavsha2/Downloads/Terraform/CTF/s3/webex.jpeg"
}

#IAM policy for Cloudfront
data "aws_iam_policy_document" "CDN"{
    statement{
        sid = "AllowCloudFrontOAI"
        effect = "Allow"
        actions = ["s3:*"]
        principals{
            type = "AWS"
            #identifiers = [aws_cloudfront_origin_access_identity.cdnaccess.s3_canonical_user_id]
            identifiers = [aws_cloudfront_origin_access_identity.cdnaccess.iam_arn]
        }
    
    resources = ["${aws_s3_bucket.ctf-content.arn}/*"]
    #resources = ["aws_s3_bucket.ctf-content.arn/*"]
    }
}

#Identity for Cloudfront
resource "aws_cloudfront_origin_access_identity" "cdnaccess" {
    comment = "Cloudfront user for S3 delivery"

}


resource "aws_s3_bucket_policy" "bucket-policy" {
    bucket = aws_s3_bucket.ctf-content.id
    policy = data.aws_iam_policy_document.CDN.json
  
}

resource "aws_cloudfront_distribution" "s3_distribution"{
    enabled = true
    origin {
        domain_name = aws_s3_bucket.ctf-content.bucket_regional_domain_name
        origin_id = local.s3_origin_id
        s3_origin_config {
            origin_access_identity = join("",
        ["origin-access-identity/cloudfront/",
        aws_cloudfront_origin_access_identity.cdnaccess.id]
      )
        }
    }
    custom_error_response {
    error_caching_min_ttl = 300
    error_code            = 403
    response_code         = 404
    response_page_path    = "/404.html"
  }
   default_cache_behavior {
    target_origin_id = local.s3_origin_id
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
    viewer_protocol_policy = "allow-all"
   }
    tags = {
        Name = "CTFCDNdistribution"
    }
    restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
  viewer_certificate {
    cloudfront_default_certificate = true
  }
}

output "cloudfrontdomain" {
    description = "cloudfront domain"
    value = aws_cloudfront_distribution.s3_distribution.domain_name

}

output "accessidentity" {
    value = aws_cloudfront_origin_access_identity.cdnaccess.cloudfront_access_identity_path
}

output "bucketpolicy"{
    value = data.aws_iam_policy_document.CDN.json
}
