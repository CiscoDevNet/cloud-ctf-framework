resource "aws_iam_user" "infra-dev" {
  name = "infra-dev"
}

resource "aws_iam_user" "infra-prod" {
  name = "infra-prod"
}

resource "aws_iam_group" "development" {
  name = "development"
}

resource "aws_iam_group" "production" {
  name = "production"
}

resource "aws_iam_group_membership" "dev" {
  name  = "dev-group-membership"
  users = [aws_iam_user.infra-dev.name]
  group = aws_iam_group.development.name
}

resource "aws_iam_group_membership" "prod" {
  name  = "tf-group1-membership"
  users = [aws_iam_user.infra-prod.name]
  group = aws_iam_group.production.name
}

resource "aws_s3_bucket" "infra-dev-secure-bucket" {
  bucket_prefix = "infra-dev-secure-bucket-"
  acl    = "private"

  tags = {
    Name = "infra-dev"
  }
}

resource "aws_s3_bucket" "infra-prod-secure-bucket" {
  bucket_prefix = "infra-prod-secure-bucket-"
  acl    = "private"

  tags = {
    Name = "infra-prod"
  }
}

resource "aws_iam_policy" "infra-dev" {
  name        = "infra-dev"
  path        = "/"

  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListAllMyBuckets",
                "s3:GetBucketLocation"
            ],
            "Resource": [
                "arn:aws:s3:::*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:*"
            ],
            "Resource": [
                "${aws_s3_bucket.infra-dev-secure-bucket.arn}",
                "${aws_s3_bucket.infra-prod-secure-bucket.arn}"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:GetObject"
            ],
            "Resource": [
                "${aws_s3_bucket.infra-dev-secure-bucket.arn}/*",
                "${aws_s3_bucket.infra-prod-secure-bucket.arn}/*"
            ]
        }
    ]
} )
}

resource "aws_iam_policy" "infra-prod" {
  name        = "infra-prod"
  path        = "/"

  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListAllMyBuckets",
                "s3:GetBucketLocation"
            ],
            "Resource": [
                "arn:aws:s3:::*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:*"
            ],
            "Resource": [
                "${aws_s3_bucket.infra-dev-secure-bucket.arn}",
                "${aws_s3_bucket.infra-prod-secure-bucket.arn}"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:GetObject"
            ],
            "Resource": [
                "${aws_s3_bucket.infra-dev-secure-bucket.arn}/*",
                "${aws_s3_bucket.infra-prod-secure-bucket.arn}/*"
            ]
        }
    ]
} )
}

resource "aws_iam_group_policy_attachment" "infra-dev" {
  group      = aws_iam_group.development.name
  policy_arn = aws_iam_policy.infra-dev.arn
}

resource "aws_iam_group_policy_attachment" "infra-prod" {
  group      = aws_iam_group.production.name
  policy_arn = aws_iam_policy.infra-prod.arn
}


output "infra-dev-policy" {
    value = aws_iam_policy.infra-dev.id
}

output "infra-prod-policy" {
    value = aws_iam_policy.infra-prod.id
}