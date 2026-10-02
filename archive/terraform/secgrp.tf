# Copyright (C) 2018-2023 Mark McIntyre
#
# Security Groups
#

resource "aws_default_security_group" "main_sg" {
  vpc_id                 = aws_vpc.ec2_vpc.id
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
    }
  ]
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    billingtag = "Management"
  }
}

resource "aws_security_group" "ec2_secgrp" {
  name        = "ec2SecurityGroup"
  description = "Security Group for EC2 instances"
  vpc_id      = aws_vpc.ec2_vpc.id
  ingress = [
    {
      cidr_blocks      = [aws_vpc.ec2_vpc.cidr_block]
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
      cidr_blocks      = ["194.0.0.0/8"]
      description      = "MariaDB"
      from_port        = 3306
      protocol         = "tcp"
      to_port          = 3306
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      security_groups  = []
      self             = false
    },
    {
      cidr_blocks      = ["0.0.0.0/0"]
      description      = "icmp"
      from_port        = -1
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      protocol         = "icmp"
      security_groups  = []
      self             = false
      to_port          = -1
    }, 
    {
        cidr_blocks      = ["0.0.0.0/0"]
        description = "mariadb"
        from_port        = 3306
        ipv6_cidr_blocks = []
        prefix_list_ids  = []
        protocol         = "tcp"
        security_groups  = []
        self             = false
        to_port          = 3306
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
  tags = {
    billingtag = "ukmda"
  }
}
/*
resource "aws_security_group" "ec2publicsg" {
  name        = "ec2PublicSG"
  description = "Public SG used by EC2"
  vpc_id      = aws_vpc.default_vpc.id
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
    }
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
  tags = {
    billingtag = "Management"
  }
}
*/