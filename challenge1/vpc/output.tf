output "vpc_id" {
    description = "vpc id"
    value = aws_vpc.ctf_challenge1_vpc.id
}

output "public_ip"{
    value= aws_subnet.my-public.map_public_ip_on_launch
}