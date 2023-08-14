##############################################################################
# Copyright (c) 2018- Mark McIntyre
##############################################################################
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
