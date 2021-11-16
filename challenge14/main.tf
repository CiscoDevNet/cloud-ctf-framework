resource "aws_iam_user" "terr-user" {
    name = "dev"
}


resource "aws_iam_user" "terr-user1" {
    name = "prod"
}

resource "aws_iam_group" "Developers" {
    name = "Developers"
}

resource "aws_iam_group" "Production" {
    name = "Production"
}


resource "aws_iam_group_membership" "Dev" {
    name = "tf-group-membership"
    users = [aws_iam_user.terr-user.name]
    group = aws_iam_group.Developers.name
}


resource "aws_iam_group_membership" "Prod" {
    name = "tf-group1-membership"
    users = [aws_iam_user.terr-user1.name]
    group = aws_iam_group.Production.name
}



resource "aws_s3_bucket" "ctf-secure-bucket"{
    bucket = "ctf-secure-bucket"
    acl="private"
    versioning{
        enabled = true
    }

     tags = {
        Name = "infra"

    }

}



resource "aws_s3_bucket_object" "files0" {
    bucket = aws_s3_bucket.ctf-secure-bucket.id
    key = "/Home/dev/dev.txt"
    source = "/Users/bhavsha2/Documents/terraform_rev/s3_chall/dev.txt"


}



resource "aws_s3_bucket_object" "files1" {
    bucket = aws_s3_bucket.ctf-secure-bucket.id
    key = "/Home/prod/prod.txt"
    source = "/Users/bhavsha2/Documents/terraform_rev/s3_chall/prod.txt"


}


data "aws_iam_policy_document" "Infra_folder" {


    version = "2012-10-17"
    statement {

        sid    = "AllowObjectOperationsInFolder"
        effect = "Allow"
        actions = [
      "s3:GetObject",
      "s3:ListBucket"
    ]
        resources = [
            
            "arn:aws:s3:::ctf-secure-bucket/Home/",
            "arn:aws:s3:::ctf-secure-bucket/Home/*"
        ]
    }
}


resource "aws_iam_group_policy" "home_folder_access"{
    group = aws_iam_group.Developers.name
    
    policy = data.aws_iam_policy_document.Infra_folder.json

}



resource "aws_iam_group_policy" "home1_folder_access"{
    group = aws_iam_group.Production.name
    
    policy = data.aws_iam_policy_document.Infra_folder.json

}