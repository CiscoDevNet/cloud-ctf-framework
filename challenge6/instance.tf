resource "aws_key_pair" "mykey"{
    key_name = "mykey"
    public_key = "${file("${var.PATH_TO_PUBLIC_KEY}")}"
    #public_key = var.PATH_TO_PUBLIC_KEY
}

resource "aws_instance" "chall1http"{
    ami = "ami-01cc34ab2709337aa"
    instance_type="t2.micro"
    key_name = aws_key_pair.mykey.key_name
    subnet_id = aws_subnet.my-public.id


    provisioner "file" {
      source      = "main.py"
      destination = "/home/ec2-user/main.py"
    }

    provisioner "remote-exec" {
      inline = [
        "pip3 install flask",
        "pip3 install requests",
        "mkdir -p /home/ec2-user/templates",
      ]
    }

    provisioner "file" {
      source      = "index.html"
      destination = "/home/ec2-user/templates/index.html"
    }

    provisioner "remote-exec" {
      inline = [
        "nohup python3 /home/ec2-user/main.py &",
        "sleep 1"
      ]
    }

    connection {
        type     = "ssh"
        user     = "ec2-user"
        password = ""
        host     = self.public_ip
        private_key = file("id_rsa")
      }
    
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






