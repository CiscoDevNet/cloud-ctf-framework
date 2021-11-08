resource "aws_iam_role" "terraformrole"{
    name = "terraformrole"
    assume_role_policy= <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
tags = {
    tag-key = "ssrf-terraformrole"
}
}

resource "aws_iam_instance_profile" "terraformprofile"{
    name = "terraformprofile"
    role = aws_iam_role.terraformrole.name
}


resource "aws_iam_role_policy" "CTF-Infra1" {
    name = "CTF-Infra1"
    role = aws_iam_role.terraformrole.id

    policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "ec2:AuthorizeSecurityGroupIngress",
                "s3:List*",
                "s3:Get*"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}

