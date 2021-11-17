#get AZ's details
data "aws_availability_zones" "availability_zones" {}
#create VPC
resource "aws_vpc" "ctf_chal5_vpc" {
  cidr_block           = "${var.vpc_cidr}"
  enable_dns_hostnames = true
  tags = {
    Name = "ctf_chal5_vpc"
  }
}

resource "aws_key_pair" "ctf_challenge5_deployer" {
  key_name   = "ctf_challenge5_deployer"
  public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC5Q/G+l6wANDsDKpn5LhOBFSAB9CgVl+nAOgVEhiMIY6fpdh0LU3Og7Q5XqieqJzW3ZMi8Q2Qwcqgf5n4nUXt/ZtxkSjKD3ZeAPG+hCD644Imo9nk0lqBxPQTK27ol70kCwf5lDOAZxoY4E21gSMGhLZFDe+Wr6nZeL1F5yAMp7fUXTzX5Fju8JxtSPiqKa+1OvxyuQXA7+c3FmVbTv/JfxxI5vsldCmveU4K07UggnEaWgdd99ZznESVY+ztnEpoed6Q4Bs05UxDdq1c/oE5Li1dSkIjd8gxphZ1e5GkvLlntmo/RuPv0MSqo1Ogjq7N4Ep+op6oC41aA1iL4qlVVmz2+O9iPjwEUcpvUAPVVr06j1fqVoswQ5ZVbW6bUcwjP0N5kdS2m7k8+u7/1piYQY/uxewjJpzcP+PTWiLHgz7Uu/ry3X8aZhXcKOKJNwj++YjMbslsv/O2s7/rbMkkabdxI0O5thHXPdr7NxRZ0TZOU6nnif1UtokcgmM983Hs= chal5-deployer@cisco.com"
}

#create public subnet
resource "aws_subnet" "ctf_chal5_vpc_public_subnet" {
  vpc_id                  = "${aws_vpc.ctf_chal5_vpc.id}"
  cidr_block              = "${var.subnet_one_cidr}"
  availability_zone       = "${data.aws_availability_zones.availability_zones.names[0]}"
  map_public_ip_on_launch = true
  tags = {
    Name = "ctf_chal5_vpc_public_subnet"
  }
}
#create private subnet one
resource "aws_subnet" "ctf_chal5_vpc_private_subnet_one" {
  vpc_id            = "${aws_vpc.ctf_chal5_vpc.id}"
  cidr_block        = "${element(var.subnet_two_cidr, 0)}"
  availability_zone = "${data.aws_availability_zones.availability_zones.names[0]}"
  tags = {
    Name = "ctf_chal5_vpc_private_subnet_one"
  }
}
#create private subnet two
resource "aws_subnet" "ctf_chal5_vpc_private_subnet_two" {
  vpc_id            = "${aws_vpc.ctf_chal5_vpc.id}"
  cidr_block        = "${element(var.subnet_two_cidr, 1)}"
  availability_zone = "${data.aws_availability_zones.availability_zones.names[1]}"
  tags = {
    Name = "ctf_chal5_vpc_private_subnet_two"
  }
}
#create internet gateway
resource "aws_internet_gateway" "ctf_chal5_vpc_internet_gateway" {
  vpc_id = "${aws_vpc.ctf_chal5_vpc.id}"
  tags = {
    Name = "ctf_chal5_vpc_internet_gateway"
  }
}
#create public route table (assosiated with internet gateway)
resource "aws_route_table" "ctf_chal5_vpc_public_subnet_route_table" {
  vpc_id = "${aws_vpc.ctf_chal5_vpc.id}"
  route {
    cidr_block = "${var.route_table_cidr}"
    gateway_id = "${aws_internet_gateway.ctf_chal5_vpc_internet_gateway.id}"
  }
  tags = {
    Name = "ctf_chal5_vpc_public_subnet_route_table"
  }
}
#create private subnet route table
resource "aws_route_table" "ctf_chal5_vpc_private_subnet_route_table" {
  vpc_id = "${aws_vpc.ctf_chal5_vpc.id}"
  tags = {
    Name = "ctf_chal5_vpc_private_subnet_route_table"
  }
}
#create default route table
resource "aws_default_route_table" "ctf_chal5_vpc_main_route_table" {
  default_route_table_id = "${aws_vpc.ctf_chal5_vpc.default_route_table_id}"
  tags                   = {
    Name = "ctf_chal5_vpc_main_route_table"
  }
}
#assosiate public subnet with public route table
resource "aws_route_table_association" "ctf_chal5_vpc_public_subnet_route_table" {
  subnet_id      = "${aws_subnet.ctf_chal5_vpc_public_subnet.id}"
  route_table_id = "${aws_route_table.ctf_chal5_vpc_public_subnet_route_table.id}"
}
#assosiate private subnets with private route table
resource "aws_route_table_association" "ctf_chal5_vpc_private_subnet_one_route_table_assosiation" {
  subnet_id      = "${aws_subnet.ctf_chal5_vpc_private_subnet_one.id}"
  route_table_id = "${aws_route_table.ctf_chal5_vpc_private_subnet_route_table.id}"
}
resource "aws_route_table_association" "ctf_chal5_vpc_private_subnet_two_route_table_assosiation" {
  subnet_id      = "${aws_subnet.ctf_chal5_vpc_private_subnet_two.id}"
  route_table_id = "${aws_route_table.ctf_chal5_vpc_private_subnet_route_table.id}"
}
#create security group for web
resource "aws_security_group" "web_security_group" {
  name        = "web_security_group"
  description = "Allow all inbound traffic"
  vpc_id      = "${aws_vpc.ctf_chal5_vpc.id}"
  tags = {
    Name = "web_security_group"
  }
}
#create security group ingress rule for web
resource "aws_security_group_rule" "web_ingress" {
  count             = "${length(var.web_ports)}"
  type              = "ingress"
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  from_port         = "${element(var.web_ports, count.index)}"
  to_port           = "${element(var.web_ports, count.index)}"
  security_group_id = "${aws_security_group.web_security_group.id}"
}
#create security group egress rule for web
resource "aws_security_group_rule" "web_egress" {
  count             = "${length(var.web_ports)}"
  type              = "egress"
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  from_port         = "${element(var.web_ports, count.index)}"
  to_port           = "${element(var.web_ports, count.index)}"
  security_group_id = "${aws_security_group.web_security_group.id}"
}
#create security group for db
resource "aws_security_group" "ctf_chal5_db_security_group" {
  name        = "ctf_chal5_db_security_group"
  description = "Allow all inbound traffic"
  vpc_id      = "${aws_vpc.ctf_chal5_vpc.id}"
  tags = {
    Name = "ctf_chal5_db_security_group"
  }
}
#create security group ingress rule for db
resource "aws_security_group_rule" "db_ingress" {
  count             = "${length(var.db_ports)}"
  type              = "ingress"
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  from_port         = "${element(var.db_ports, count.index)}"
  to_port           = "${element(var.db_ports, count.index)}"
  security_group_id = "${aws_security_group.ctf_chal5_db_security_group.id}"
}
#create security group egress rule for db
resource "aws_security_group_rule" "db_egress" {
  count             = "${length(var.db_ports)}"
  type              = "egress"
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  from_port         = "${element(var.db_ports, count.index)}"
  to_port           = "${element(var.db_ports, count.index)}"
  security_group_id = "${aws_security_group.ctf_chal5_db_security_group.id}"
}
#create EC2 instance
resource "aws_instance" "ctf_chal5_web_instance" {
  ami                    = lookup(var.images , var.AWS_REGION)
  instance_type          = "t2.micro"
  key_name               = "ctf_challenge5_deployer"
  vpc_security_group_ids = ["${aws_security_group.web_security_group.id}"]
  subnet_id              = "${aws_subnet.ctf_chal5_vpc_public_subnet.id}"
  tags                   = {
    Name = "ctf_chal5_web_instance"
  }
  volume_tags            = {
    Name = "ctf_chal5_web_instance_volume"
  }
  provisioner "remote-exec" {
    #install apache, mysql client, php
    inline = [
      "sudo yum update -y",
      "sudo amazon-linux-extras install -y lamp-mariadb10.2-php7.2 php7.2",
      "sudo yum install -y httpd mariadb-server",
      "sudo systemctl start httpd",
      "sudo systemctl enable httpd",
      "sudo usermod -a -G apache ec2-user",
      "sudo chown -R apache:apache /var/www",
      "sudo chmod 775 /var/www",
      "sudo chmod 775 /var/www/html",
      "ln -s /var/www/.maria /var/www/html/.maria"
    ]
  }
  provisioner "file" {
    #copy the index file form local to remote
    source      = "index.php"
    destination = "/var/www/html/index.php"
  }

  provisioner "file" {
    #copy the db_creds.php file form local to remote
    source      = "db_creds.php"
    destination = "/var/www/db_creds.php"
  }

  provisioner "remote-exec" {
    inline = [
      "sudo chattr +i /var/www/db_creds.php",
      "sudo chattr +i /var/www/html/index.php"
    ]
  }

  connection {
    type        = "ssh"
    user        = "ec2-user"
    password    = ""
    host = self.public_ip
    #copy <your_private_key>.pem to your local instance home directory
    #restrict permission: chmod 400 <your_private_key>.pem
    private_key = "${file("/opt/CloudCTF/challenge5/web_ssh_private_key.pem")}"
  }
}
#create aws rds subnet groups
resource "aws_db_subnet_group" "ctf_chal5_database_subnet_group" {
  name       = "chal5dbsg"
  subnet_ids = [
    "${aws_subnet.ctf_chal5_vpc_private_subnet_one.id}", "${aws_subnet.ctf_chal5_vpc_private_subnet_two.id}"
  ]
  tags       = {
    Name = "ctf_chal5_database_subnet_group"
  }
}
#create aws mysql rds instance
resource "aws_db_instance" "ctf_chal5_database_instance" {
  allocated_storage      = 5
  storage_type           = "gp2"
  engine                 = "mariadb"
  engine_version         = "10.5.12"
  instance_class         = "db.t2.micro"
  port                   = 3306
  vpc_security_group_ids = ["${aws_security_group.ctf_chal5_db_security_group.id}"]
  db_subnet_group_name   = "${aws_db_subnet_group.ctf_chal5_database_subnet_group.name}"
  name                   = "chal5db"
  identifier             = "ctf-chal5-sqldb"
  username               = "chal5user"
  password               = "cH41l3ng3_5"
  skip_final_snapshot    = true
  tags                   = {
    Name = "ctf_chal5_database_instance"
  }
}
#output webserver and dbserver address
output "db_server_address" {
  value = "${aws_db_instance.ctf_chal5_database_instance.address}"
}
output "web_server_address" {
  value = "${aws_instance.ctf_chal5_web_instance.public_dns}"
}