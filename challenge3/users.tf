provider "aws" { 
    region = "ap-south-1"
}


locals {
    group_name = "Avengers"
    users = [
        "captain.lewis",
        "captain1.polo",
        "captain2.treadway"
    ]
}

#S3 bucket
resource "aws_s3_bucket" "ussssser-content"{
    bucket = "ussssser-content"
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
        Name = "user_content"

    }
}

terraform {
  backend "s3" {
      key = "global/iam/groups/terraform.tfstate"
      bucket = "ctf-content"
      region = "ap-south-1"

  }
}

#S3 bucket files
resource "aws_s3_bucket_object" "files0" {
    bucket = aws_s3_bucket.ussssser-content.id
    key = "Home/webex.jpeg"
    source = "/Users/bhavsha2/Downloads/Terraform/CTF/s3/webex.jpeg"
}
#S3 bucket files1
resource "aws_s3_bucket_object" "files1" {
    bucket =aws_s3_bucket.ussssser-content.id
    key = "Home/captain.lewis/cyber.jpeg"
    source = "/Users/bhavsha2/Downloads/Terraform/CTF/iam/cyber.jpeg"
}
#S3 bucket files2

resource "aws_s3_bucket_object" "files2" {
    bucket = aws_s3_bucket.ussssser-content.id
    key = "Home/captain1.polo/cyber.jpeg"
    source = "/Users/bhavsha2/Downloads/Terraform/CTF/iam/cyber.jpeg"
}

#S3 bucket files3
resource "aws_s3_bucket_object" "files3" {
    bucket = aws_s3_bucket.ussssser-content.id
    key = "Home/captain2.treadway/cyber.jpeg"
    source = "/Users/bhavsha2/Downloads/Terraform/CTF/iam/cyber.jpeg"
}

#S3 bucket files4

resource "aws_s3_bucket_object" "files4" {
    bucket = aws_s3_bucket.ussssser-content.id
    key = "Home/tac_user/cyber.jpeg"
    source = "/Users/bhavsha2/Downloads/Terraform/CTF/iam/cyber.jpeg"
}

#S3 bucket files5

resource "aws_s3_bucket_object" "files5" {
    bucket = aws_s3_bucket.ussssser-content.id
    key = "Home/tac_user1/cyber.jpeg"
    source = "/Users/bhavsha2/Downloads/Terraform/CTF/iam/cyber.jpeg"
}
#S3 bucket files6
resource "aws_s3_bucket_object" "files6" {
    bucket = aws_s3_bucket.ussssser-content.id
    key = "Home/ps_user/cyber.jpeg"
    source = "/Users/bhavsha2/Downloads/Terraform/CTF/iam/cyber.jpeg"
}

data "aws_iam_policy_document" "avengers_group" {
    statement {
        sid = "ConsoleAccess"
        effect = "Allow"
        actions = [
            "s3:GetAccountPublicAccessBlock",
            "s3:GetBucketAcl",
            "s3:GetBucketLocation",
            "s3:GetBucketPolicyStatus",
            "s3:GetBucketPublicAccessBlock",
            "s3:ListAllMyBuckets",
        ]
        resources = ["*"]

    }
    statement {
        sid = "ListObjectsInBucket"
        effect = "Allow"
        actions   = ["s3:ListBucket"]
        resources = ["*"]
    }
}

resource "aws_iam_group" "Avengers"{
    name = local.group_name
    path = "/"
}

resource "random_string" "tracker" {
  length           = 16
  upper            = true
  number           = false
  special          = true
  override_special = "/@£$"
}

resource "aws_iam_group_policy" "Avengers-policy-group" {
    group = aws_iam_group.Avengers.id
    policy = data.aws_iam_policy_document.avengers_group.json

  
}

resource "aws_iam_user" "avenger_user" {
    for_each = toset(local.users)
    name = each.value
    path = "/"
    tags = {
        tracker = sha512(random_string.tracker.result)
    }
  
}



resource "aws_iam_user_group_membership" "Avengers_user" {
    for_each = aws_iam_user.avenger_user
    user = each.value.name
    groups = [aws_iam_group.Avengers.name]
}

resource "aws_iam_access_key" "Avenger_user" {
    for_each = aws_iam_user.avenger_user
    user = each.value.name
}


output "access-keys" {
    description = "List of access keys and secret access keys"
    value = {
        for k,v in aws_iam_access_key.Avenger_user : v.user => [v.id , v.secret]
    }
}

output "arn" {
    description = "s3 bucket arn"
    value = aws_s3_bucket.ussssser-content.arn
}


#from groups

locals {
    ctf_bucket = data.terraform_remote_state.Avengers.outputs.arn
    groups = [
        "TAC",
        "PS"    
    ]
    user_comp = [
        "tac_user",
        "tac_user1",
        "ps_user",
        "ps_user1",
        "classic_user"
    ]
}

resource "aws_iam_user" "comp_user" {
    for_each = toset(local.user_comp)
    name = each.value
    path = "/"
}
resource "aws_iam_group" "comp" {
    for_each = toset(local.groups)
    name = each.key 
    path = "/"

  
}

data "terraform_remote_state" "Avengers"{
    backend = "s3"
    config = {
        bucket = "ctf-content"
        key = "global/iam/groups/terraform.tfstate"
        region = "ap-south-1"


    }
}

resource "aws_iam_group_membership" "TAC" {
    name = local.groups[0]
    users = [local.user_comp[0],local.user_comp[1]]
    group = local.groups[0]
  
}

resource "aws_iam_group_membership" "PS" {
    name = local.groups[1]
    users = [local.user_comp[2],local.user_comp[3]]
    group = local.groups[1]
}


data "aws_iam_policy_document" "home_folder" {
    statement {
      sid = "AllowFolder"
      effect = "Allow"
      actions = [
          "s3:ListBucket",
      ]
      resources = [local.ctf_bucket]
      condition {
        test = "StringEquals"
        variable = "s3:prefix"
        values = ["data/", "data/$${aws:username}/*"]
      }
      condition {
        test = "StringEquals"
        variable = "s3:delimiter"
        values = ["/"]
      }

    }
    statement {
      sid = "AllowObject"
      effect = "Allow"
      actions = ["s3:*"]
      resources = [
          "${local.ctf_bucket}/Home/",
          "${local.ctf_bucket}/Home/*"
      ]
    }
}

data "aws_iam_policy_document" "tac_folder" {
  version = "2012-10-17"
  statement {
    sid    = "AllowListFolderContent"
    effect = "Allow"
    actions = [
      "s3:ListBucket",
    ]
    resources = [local.ctf_bucket]
    condition {
      test     = "StringEquals"
      variable = "s3:prefix"
      values   = ["TACDepartment/", "TACDepartment/*"]
    }
    condition {
      test     = "StringEquals"
      variable = "s3:delimiter"
      values   = ["/"]
    }
  }
  statement {
    sid    = "AllowObjectOperationsInFolder"
    effect = "Allow"
    actions = [
      "s3:*Object",
    ]
    resources = [
      "${local.ctf_bucket}/TACDepartment/*",
      "${local.ctf_bucket}/TACDepartment/",
    ]
  }
}
resource "aws_iam_group_policy" "home_folder_access" {
    for_each = aws_iam_group.comp
    group = each.key 
    policy = data.aws_iam_policy_document.home_folder.json
  
}

resource "aws_iam_group_policy" "tac_folder_access"{
    group = aws_iam_group.comp["TAC"].id
    policy = data.aws_iam_policy_document.tac_folder.json
}

