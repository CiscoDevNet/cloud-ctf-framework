resource "aws_instance" "chall1http"{
    ami = "ami-041d6256ed0f2061c"
    instance_type="t2.micro"
    subnet_id = aws_subnet.my-public.id
    security_groups=[aws_security_group.vpc_security_group.id]
    user_data  = <<EOF
    #!/bin/bash
    yum update -y 
    yum install -y httpd
    systemctl start httpd
    systemctl enable httpd
    echo "<h1> 
           <p>This is the secure page where only few can access . Below is the secure conversation 
           <br>asd272727: where is the secure doc?
           <br>bgsgsgsgsg: I think only admin can access it
           <br>rfc5785 : I think super admin can access it
           <br>john78567: I cannot find it
           <br>bh76363636: Tell us
           </p>
        </h1> " > /var/www/html/index.html
    EOF
    tags = merge(
    var.additional_tags,
    {
      Name = "CloudCTFchall1"
    },
    )
}






