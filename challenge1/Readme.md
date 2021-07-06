
Challenge 1:

Security Misconfiguration : This challenge shows the incorrect configuration in deploying vpc with default nacl

Vulnerability : the default nacl which gets applied to vpc allows all traffic

below is the vulnerable code in main.tf in vpc 

resource "aws_default_network_acl" "default"

{
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

Solution: 

resource "aws_default_network_acl" "default" {
    default_network_acl_id = aws_vpc.ctf-vpc.default_network_acl_id
    
  }
