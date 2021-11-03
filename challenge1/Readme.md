
Challenge 1:

Security Misconfiguration : This challenge shows the incorrect configuration in deploying vpc with default nacl

Vulnerability : the default nacl which gets applied to vpc allows all traffic. The allow all rule is at top while the other specific rules are at bottom.

below is the vulnerable code in main.tf in vpc . The idea here is that only 106.203.219.180 should be accessing the web application. 


resource "aws_default_network_acl" "default"
{
    default_network_acl_id = aws_vpc.ctf_challenge1_vpc.default_network_acl_id
    
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

Solution: 

1) Either delete the any rule or put it at the end so that only the public ip specified can access the application port 80 
