
locals {
  ports_in = [
    0
  ]
  ports_out = [
    0
  ]
}

resource "aws_vpc" "ctf_challenge1_vpc" {
    cidr_block ="10.0.0.0/16"
    #instance_tenancy = "default"
    enable_dns_support = "true"
    enable_dns_hostnames = "true"
    enable_classiclink = "false"
    tags = merge(
    var.additional_tags,
    {
      Name = "ctf_challenge1_vpc"
    },
    )
}




resource "aws_default_network_acl" "default" {
    default_network_acl_id = aws_vpc.ctf_challenge1_vpc.default_network_acl_id
    tags = merge(
    var.additional_tags,
    {
      Name = "ctf_challenge1_nacl"
    },
    )
    ingress{
        protocol = -1
        rule_no = 100
        action = "allow"
        cidr_block = "0.0.0.0/0"
        from_port = 0
        to_port = 0

    }
    ingress{
        cidr_block = "20.20.20.20/32"
        rule_no = 110
        action="allow"
        from_port = 22
        to_port = 22
        protocol="tcp"
    }
    ingress{
        cidr_block = "40.40.40.40/32"
        rule_no = 120
        action="allow"
        from_port = 443
        to_port = 443
        protocol="tcp"
            
    }
    ingress{
        cidr_block = "106.203.219.180/32"
        rule_no = 130
        action = "allow"
        protocol = "tcp"
        from_port = 80
        to_port = 80
    }
    egress{
        protocol = -1
        rule_no = 100
        action = "allow"
        cidr_block = "0.0.0.0/0"
        from_port = 0
        to_port = 0
        
    }   
}

###Subnets 
#This is a public subnet 
resource "aws_subnet" "my-public" {
    vpc_id = aws_vpc.ctf_challenge1_vpc.id
    cidr_block = "10.0.1.0/24"
    map_public_ip_on_launch = "true"
    availability_zone = "ap-south-1a"
    tags = merge(
    var.additional_tags,
    {
      Name = "ctf-public-1"
    },
    )
}

#This is a private subnet
resource "aws_subnet" "my-private" {
    vpc_id = aws_vpc.ctf_challenge1_vpc.id
    cidr_block = "10.0.2.0/24"
    map_public_ip_on_launch = "false"
    availability_zone = "ap-south-1a"
    tags = merge(
    var.additional_tags,
    {
      Name = "ctf-private-1"
    },
    )  
}

#Internet GW
resource "aws_internet_gateway" "main-igw" {
    vpc_id = aws_vpc.ctf_challenge1_vpc.id
    tags = merge(
    var.additional_tags,
    {
      Name = "CTFInternetGW"
    },
    ) 
}

#Route table 
#This basically calls the Internet gateway 
resource "aws_route_table" "main-public" {
    vpc_id = aws_vpc.ctf_challenge1_vpc.id
    route {
        cidr_block = "0.0.0.0/0"
        gateway_id = aws_internet_gateway.main-igw.id
    }
    tags = merge(
    var.additional_tags,
    {
      Name = "ctf-public-internet"
    },
    )
}

#Route association 
#This basically associates the rouute to internet gateway i...e setting default route for the internet 
resource "aws_route_table_association" "main-public-1-a" {
    subnet_id = aws_subnet.my-public.id
    route_table_id = aws_route_table.main-public.id
}

resource "aws_eip" "nat" {
    vpc = true
    tags = merge(
    var.additional_tags,
    {
      Name = "ctf-challenge1_eip"
    },
    )
}

#NAt GAteway 
resource "aws_nat_gateway" "nat-gw" {
    allocation_id = aws_eip.nat.id
    subnet_id = aws_subnet.my-public.id
    depends_on = [aws_internet_gateway.main-igw]
    tags = merge(
    var.additional_tags,
    {
      Name = "ctf-challenge1_nat"
    },
    )
}

#VPC Setup for NAT
resource "aws_route_table" "main-private" {
    vpc_id = aws_vpc.ctf_challenge1_vpc.id
    route {
        cidr_block = "0.0.0.0/0"
        nat_gateway_id = aws_nat_gateway.nat-gw.id
    }
    tags = merge(
    var.additional_tags,
    {
        Name = "nat-gw-private"
    },
    )  
}

#Route association private 
resource "aws_route_table_association" "main-private-1-a" {
    subnet_id = aws_subnet.my-private.id
    route_table_id = aws_route_table.main-private.id 
}



resource "aws_security_group" "vpc_security_group"{
    name = "ctf_security_group"
    vpc_id = aws_vpc.ctf_challenge1_vpc.id
    tags = merge(
    var.additional_tags,
    {
        Name = "ctf-challenge1_sg"
    },
    ) 
    dynamic "ingress"{
        for_each = toset(local.ports_in)
        content{
        description = "inbound to Ec2"
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = ["0.0.0.0/0"]
        }
    }

    dynamic "egress"{
        for_each = toset(local.ports_out)
        content{
        description = "inbound to Ec2"
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = ["0.0.0.0/0"]
        }
    }
}

