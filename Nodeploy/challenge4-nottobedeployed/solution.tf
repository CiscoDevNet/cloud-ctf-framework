provider "aws" {
    region = var.AWS_REGION


}

locals {
    ssm-dbConnection = "arn:aws:ssm:${var.AWS_REGION}:*:parameter/dbConnection"
    ssm-dbUsername = "arn:aws:ssm:var:${var.AWS_REGION}:*:parameter/dbUsername"
    ssm-dbPassword = "arn:aws:ssm:var:${var.AWS_REGION}:*:parameter/dbPassword"
}


data "aws_iam_policy_document" "trustpolicy" {
    statement {
      effect= "Allow"
      principals {
          type = "Service"
          identifiers = ["ec2.amazonaws.com"]

      }
      actions = [
          "sts:AssumeRole"
      ]
    }

}

resource "aws_iam_role" "webserver" {
    name = "ctf-webserver"
    assume_role_policy = data.aws_iam_policy_document.trustpolicy.json
  
}

data "aws_iam_policy_document" "webserver"{
    statement {
        effect = "Allow"
        actions = [
            "ssm:GetParameter"
        ]
        resources = [
            local.ssm-dbConnection,
            local.ssm-dbUsername,
            local.ssm-dbPassword    

        ]
    }

  statement  {
       effect = "Allow"
       actions = [
           "ssm:DescribeParameters"
       ]
       resources = [
           "*"
       ]
    }
    
}

resource "aws_iam_policy" "webserver" {
    name = "ctf-webserver"
    policy = data.aws_iam_policy_document.webserver.json 
  
}

resource "aws_iam_policy_attachment" "webserver" {
    name = "ctf-webserver"
    roles = [aws_iam_role.webserver.name]
    policy_arn = aws_iam_policy.webserver.arn

  
}

resource "aws_iam_instance_profile" "webserver" {
    name = "webserver"
    role = aws_iam_role.webserver.name 
  
} 

resource "aws_instance" "webserver-soln" {
    ami = "ami-0c1a7f89451184c8b"
    instance_type = "t2.micro"
    iam_instance_profile = aws_iam_instance_profile.webserver.name
    key_name = aws_key_pair.mykey.key_name
    tags = {
        Name = "webserver-soln"


    }
  
}

resource "aws_key_pair" "mykey" {
    key_name = "mykey2"
    public_key = file(var.PATH_TO_PUBLIC_KEY)
  
}


output "ssm"{
    value = "arn:aws:ssm:${var.AWS_REGION}:*:parameter/dbConnection"
}
