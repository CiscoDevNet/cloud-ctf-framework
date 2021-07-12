Security Misconfiguration:
This challenges talks on the error in iam policy for the S3 bucket 

Vulnerability : 

data "aws_iam_policy_document" "CDN"{
    statement{
        sid = "AllowCloudFrontOAI"
        effect = "Allow"
        actions = ["s3:*"]-----------> basically gives all permission on the s3 object 
        principals{
            type = "AWS"
            #identifiers = [aws_cloudfront_origin_access_identity.cdnaccess.s3_canonical_user_id]
            identifiers = [aws_cloudfront_origin_access_identity.cdnaccess.iam_arn]
        }
    
    resources = ["${aws_s3_bucket.ctf-content.arn}/*"]
    #resources = ["aws_s3_bucket.ctf-content.arn/*"]
    }
}


Fix: 
actions = ["s3:GetObject"]
