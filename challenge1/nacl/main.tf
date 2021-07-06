resource "aws_network_acl" "mynacl" {
  
    vpc_id = var.vpc_id
  
  
}

resource "aws_network_acl_rule" "public_outbound_all" {
    network_acl_id = aws_network_acl.mynacl.id
    cidr_block = "0.0.0.0/0"
    rule_number = 100
    protocol = "all"
    rule_action = "allow"
    egress=true

}

resource "aws_network_acl_rule" "public_inbound_SSH" {
    network_acl_id = aws_network_acl.mynacl.id
    cidr_block = "20.20.20.20/32"
    rule_number = 100
    protocol = "tcp"
    rule_action = "allow"
    egress=false
    from_port = 22
    to_port = 22

  
}

resource "aws_network_acl_rule" "public_inbound_HTTPS" {
    network_acl_id = aws_network_acl.mynacl.id
    cidr_block = "0.0.0.0/0"
    rule_number = 110
    protocol = "tcp"
    rule_action = "allow"
    egress=false
    from_port = 443
    to_port = 443

  
}

resource "aws_network_acl_rule" "public_inbound_HTTP" {
    network_acl_id = aws_network_acl.mynacl.id
    cidr_block = "0.0.0.0/0"
    rule_number = 120
    protocol = "tcp"
    rule_action = "allow"
    egress=false
    from_port = 80
    to_port = 80

  
}

resource "aws_network_acl_rule" "private_inbound_SSH" {
    network_acl_id = aws_network_acl.mynacl.id
    cidr_block = "10.0.2.20/32"
    rule_number = 130
    protocol = "tcp"
    rule_action = "allow"
    egress=false
    from_port = 22
    to_port = 22

  
}
