resource "aws_vpc" "ctf-vpc" {
    cidr_block ="10.0.0.0/16"
    instance_tenancy = "default"
    enable_dns_support = "true"
    enable_dns_hostnames = "true"
    enable_classiclink = "false"
    tags = {
      Name = "CTF"
    }
  
}


resource "aws_default_network_acl" "default" {
    default_network_acl_id = aws_vpc.ctf-vpc.default_network_acl_id
    ingress{
        protocol = -1
        rule_no = 100
        action = "allow"
        cidr_block = "0.0.0.0/0"
        from_port = 0
        to_port = 0

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
#Subnets 
resource "aws_subnet" "my-public" {
    vpc_id = aws_vpc.ctf-vpc.id
    cidr_block = "10.0.1.0/24"
    map_public_ip_on_launch = "true"
    availability_zone = "ap-south-1a"
    tags = {
        Name = "main-public-1"
    }

  
}

resource "aws_subnet" "my-private" {
    vpc_id = aws_vpc.ctf-vpc.id
    cidr_block = "10.0.2.0/24"
    map_public_ip_on_launch = "false"
    availability_zone = "ap-south-1a"
    tags = {
      Name = "main-private-1"
    }

  
}

#Internet GW
resource "aws_internet_gateway" "main-igw" {
    vpc_id = aws_vpc.ctf-vpc.id
    tags = {
        Name = "InternetGW"
    }
  
}

#Route table
resource "aws_route_table" "main-public" {
    vpc_id = aws_vpc.ctf-vpc.id
    route {
        cidr_block = "0.0.0.0/0"
        gateway_id = aws_internet_gateway.main-igw.id

    }
    tags = {
        Name = "main-public-internet"
    }
}

#Route association 
resource "aws_route_table_association" "main-public-1-a" {
    subnet_id = aws_subnet.my-public.id
    route_table_id = aws_route_table.main-public.id
  
}

resource "aws_eip" "nat" {
    vpc = true
  
}

#NAt GAteway 

resource "aws_nat_gateway" "nat-gw" {
    allocation_id = aws_eip.nat.id
    subnet_id = aws_subnet.my-public.id
    depends_on = [aws_internet_gateway.main-igw]
  
}

#VPC Setup for NAT
resource "aws_route_table" "main-private" {
    vpc_id = aws_vpc.ctf-vpc.id
    route {
        cidr_block = "0.0.0.0/0"
        nat_gateway_id = aws_nat_gateway.nat-gw.id

    }
    tags = {
        Name = "nat-gw-private"
    }
  
}

#Route association private 
resource "aws_route_table_association" "main-private-1-a" {
    subnet_id = aws_subnet.my-private.id
    route_table_id = aws_route_table.main-private.id
}

#AWS_route table
resource "aws_route" "public" {
    route_table_id = aws_route_table.main-public.id
    destination_cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main-igw.id
  
}

output "vpc_id" {
    description = "vpc id"
    value = aws_vpc.ctf-vpc.id
}
