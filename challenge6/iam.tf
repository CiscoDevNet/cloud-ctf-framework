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
    tag-key = "terraformrole"
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
                "ec2:DeleteSubnet",
                "ec2:DescribeInstances",
                "ec2:CreateKeyPair",
                "ec2:AttachInternetGateway",
                "ec2:AssociateRouteTable",
                "ec2:DeleteRouteTable",
                "ec2:DescribeInternetGateways",
                "ec2:GetLaunchTemplateData",
                "ec2:StartInstances",
                "ec2:CreateNetworkInterfacePermission",
                "ec2:RevokeSecurityGroupEgress",
                "ec2:CreateRoute",
                "ec2:CreateInternetGateway",
                "ec2:DescribeScheduledInstanceAvailability",
                "ec2:DeleteInternetGateway",
                "ec2:DescribeKeyPairs",
                "ec2:DescribeRouteTables",
                "ec2:DescribeLaunchTemplates",
                "ec2:ImportKeyPair",
                "ec2:CreateTags",
                "ec2:CreateRouteTable",
                "ec2:RunInstances",
                "ec2:DetachInternetGateway",
                "ec2:DescribeInstanceEventWindows",
                "ec2:DisassociateRouteTable",
                "ec2:DescribeInstanceCreditSpecifications",
                "ec2:RevokeSecurityGroupIngress",
                "iam:*",
                "s3:PutObject",
                "s3:GetObject",
                "ec2:DescribeSecurityGroupRules",
                "ec2:DescribeInstanceTypes",
                "ec2:DeleteNatGateway",
                "ec2:*",
                "ec2:DeleteVpc",
                "ec2:CreateSubnet",
                "ec2:DescribeSubnets",
                "ec2:DeleteKeyPair",
                "ec2:DescribeAddresses",
                "ec2:DeleteTags",
                "ec2:CreateNatGateway",
                "ec2:DescribeInstanceAttribute",
                "ec2:CreateVpc",
                "ec2:DescribeVpcAttribute",
                "s3:GetBucketPolicy",
                "ec2:ModifySubnetAttribute",
                "ec2:DescribeInstanceTypeOfferings",
                "ec2:DescribeNetworkInterfaces",
                "ec2:CreateSecurityGroup",
                "sts:DecodeAuthorizationMessage",
                "ec2:ModifyVpcAttribute",
                "ec2:DeleteLaunchTemplateVersions",
                "ec2:ModifyReservedInstances",
                "ec2:DescribeInstanceStatus",
                "ec2:ReleaseAddress",
                "ec2:ModifyInstanceMetadataOptions",
                "ec2:AuthorizeSecurityGroupEgress",
                "ec2:DeleteLaunchTemplate",
                "ec2:TerminateInstances",
                "ec2:ImportInstance",
                "ec2:CreateLocalGatewayRoute",
                "ec2:DeleteRoute",
                "ec2:DescribeLaunchTemplateVersions",
                "ec2:DescribeNatGateways",
                "ec2:DescribeInstanceEventNotificationAttributes",
                "ec2:AllocateAddress",
                "ec2:DescribeSecurityGroups",
                "ec2:CreateLaunchTemplateVersion",
                "ec2:CreateLaunchTemplate",
                "ec2:DescribeVpcs",
                "ec2:DeleteSecurityGroup",
                "ec2:ModifyLaunchTemplate"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}

