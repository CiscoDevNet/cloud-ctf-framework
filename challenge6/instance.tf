

resource "aws_instance" "chall1http"{
    ami = "ami-041d6256ed0f2061c"
    instance_type="t2.micro"
    subnet_id = aws_subnet.my-public.id
    
    security_groups=[aws_security_group.vpc_security_group.id]
    iam_instance_profile=aws_iam_instance_profile.terraformprofile.name
    
    metadata_options {
      http_endpoint = "enabled"
      http_tokens = "optional"
    }
    tags = {
    Name = "SSRF"
  }
}





