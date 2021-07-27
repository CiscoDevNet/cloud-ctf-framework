Data Access

This challenge talks about the SSM vault being created by one user and it needs to be made sure that everyone does not have access to it 

In the problem challenge the username and password is stored in ssm as part of terraform which exposes the credentials being tracked in tfstate file

In the challenge the user name/password is being referenced in user-data as part of environment variable which is highly not recommended 

ref----https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-paramstore-access.html
Vulnerability########


resource "aws_ssm_parameter" "db-connection"{
    name = "dbConnection"
    value = "dbConnection"
    type  = "String"
    
}

resource "aws_ssm_parameter" "db-password"{
    name = "dbPassword"
    value = "dbPassword"
    type  = "String"
    
   
}


resource "aws_ssm_parameter" "db-username"{
    name = "dbUsername"
    value= "dbUsername"
    type  = "String"
   
    
    
    
}

data "template_file" "init" {
    template = "${file("./bootstrap.sh")}"
    vars = {
        dbConnection = aws_ssm_parameter.db-connection.value
        dbUsername = aws_ssm_parameter.db-username.value
        dbPassword = aws_ssm_parameter.db-password.value
    }
}


resource "aws_instance" "web" {
    ami = "ami-0c1a7f89451184c8b"
    instance_type = "t2.micro"
    user_data = data.template_file.init.rendered-------------> vuln
    key_name = aws_key_pair.mykey.key_name
    tags = {
        Name = "webserver"
    }
  
}

resource "aws_key_pair" "mykey" {
    key_name = "mykey"
    public_key = file(var.PATH_TO_PUBLIC_KEY)
  
}
 output "user" {
     value = aws_ssm_parameter.db-username.arn
 }


 output "password" {
     value = aws_ssm_parameter.db-password.arn
 }


 output "connection" {
     value = aws_ssm_parameter.db-connection.arn
 }

 
