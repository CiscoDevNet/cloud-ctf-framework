Access Control 
This challenge talks on missing function level access control on resources 

In this challenges there are differen groups created and in one the group policy due to incorrectly configured (as it does enforce user folder access restriction). Any user can access
other user home folder 

Vulnerability in "aws_iam_policy_document" "home_folder"



data "aws_iam_policy_document" "home_folder"
{
    statement 
    
    {
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

Solution : 

statement {
      sid = "AllowObject"
      effect = "Allow"
      actions = ["s3:*"]
      resources = [
          "${local.ctf_bucket}/Home/$${aws:username}",
          "${local.ctf_bucket}/Home/$${aws:username}/*"
      ]
    }
}
