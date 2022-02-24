#
# Security Groups
#

resource "aws_security_group" "default" {
  name                   = "default"
  description            = "default VPC security group"
  vpc_id                 = aws_vpc.main_vpc.id
  revoke_rules_on_delete = false
  ingress = [
    {
      description      = "http in"
      from_port        = 80
      to_port          = 80
      protocol         = "tcp"
      cidr_blocks      = ["0.0.0.0/0"]
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      security_groups  = []
      self             = false
    },
    {
      cidr_blocks      = ["86.0.0.0/8"]
      description      = "SSH for Admin"
      from_port        = 22
      protocol         = "tcp"
      to_port          = 22
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      security_groups  = []
      self             = false
    },
    {
      cidr_blocks      = []
      description      = "traffic from sg20192"
      from_port        = 0
      protocol         = "-1"
      self             = true
      to_port          = 0
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      security_groups  = []
    },
    {
      cidr_blocks      = []
      description      = "echo from sg8115c"
      from_port        = 8
      protocol         = "icmp"
      security_groups  = [aws_security_group.launch-wizard-4.id]
      to_port          = -1
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      self             = false
    }
  ]
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "launch-wizard-4" {
  name        = "launch-wizard-4"
  description = "launch-wizard-4 created 2020-02-10T21:59:13.598+00:00"
  vpc_id      = aws_vpc.main_vpc.id
  ingress = [
    {
      cidr_blocks      = ["0.0.0.0/0"]
      description      = "SSH for Admin"
      from_port        = 22
      protocol         = "tcp"
      to_port          = 22
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      security_groups  = []
      self             = false
    },
    {
      cidr_blocks      = []
      description      = "NFS"
      from_port        = 2049
      protocol         = "tcp"
      to_port          = 2049
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      security_groups  = []
      self             = true
    },
  ]
  egress = [
    {
      cidr_blocks      = ["0.0.0.0/0"]
      description      = ""
      from_port        = 0
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      protocol         = "-1"
      security_groups  = []
      self             = false
      to_port          = 0
    },
  ]
}

resource "aws_security_group" "launch-wizard-6" {
  name        = "launch-wizard-6"
  description = "launch-wizard-6 created 2021-10-12T18:00:55.768+01:00"
  vpc_id      = aws_vpc.main_vpc.id
  ingress = [
    {
      cidr_blocks = [
        "0.0.0.0/0",
      ]
      description = "Unsure"
      from_port   = 80
      ipv6_cidr_blocks = [
        "::/0",
      ]
      prefix_list_ids = []
      protocol        = "tcp"
      security_groups = []
      self            = false
      to_port         = 80
    },
    {
      cidr_blocks = [
        "86.0.0.0/8",
      ]
      description      = "SSH for admin"
      from_port        = 22
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      protocol         = "tcp"
      security_groups  = []
      self             = false
      to_port          = 22
    },
    {
      cidr_blocks      = []
      description      = "SSH from other nodes"
      from_port        = 22
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      protocol         = "tcp"
      security_groups = [aws_security_group.launch-wizard-4.id]
      self    = false
      to_port = 22
    },
    {
      cidr_blocks      = []
      description      = "TCP from other nodes"
      from_port        = 0
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      protocol         = "tcp"
      security_groups = [aws_security_group.default.id]
      self    = false
      to_port = 65535
    },
    {
      cidr_blocks      = []
      description      = "Testing if up"
      from_port        = 0
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      protocol         = "icmp"
      security_groups = [aws_security_group.launch-wizard-4.id]
      self    = false
      to_port = -1
  }, ]
  egress = [
    {
      cidr_blocks      = ["0.0.0.0/0"]
      description      = ""
      from_port        = 0
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      protocol         = "-1"
      security_groups  = []
      self             = false
      to_port          = 0
    },
  ]
}
