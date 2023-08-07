# Copyright (C) 2018-2023 Mark McIntyre

resource "aws_instance" "calc_server" {
  ami                    = "ami-0e37df1ded87f1f10" # Calcserver AMI cloned from MM account
  instance_type          = "c6g.4xlarge"
  iam_instance_profile   = aws_iam_instance_profile.S3FullAccess.name
  key_name               = aws_key_pair.marks_key.key_name
  tags = {
    "Name"       = "Calcengine"
    "billingtag" = "ukmon"
  }
  root_block_device {
    tags = {
      "Name"       = "calcengine"
      "billingtag" = "ukmon"
    }
    volume_size = 100
  }
  network_interface {
    network_interface_id = aws_network_interface.calcserver_if.id
    device_index         = 0
  }
}

# elastic IP attached to the calcserver
#resource "aws_eip" "calcserver" {
#  instance = aws_instance.calc_server.id
#  vpc      = true
#  tags = {
#    billingtag = "ukmon"
#  }
#}

# elastic network interface attached to the calc server

resource "aws_network_interface" "calcserver_if" {
  subnet_id                 = aws_subnet.ec2_subnet.id
  description               = "Primary network interface"
  private_ips               = [var.calcserverip]
  security_groups           = [aws_security_group.ec2_secgrp.id]
  ipv6_address_list_enabled = false
  tags = {
    "Name"       = "calcengine"
    "billingtag" = "ukmon"
  }
}


