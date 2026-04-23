# Copyright (C) 2018-2023 Mark McIntyre

resource "aws_instance" "batchserver" {
  ami                  = "ami-06f0cf249257c89b3"
  instance_type        = "t4g.micro"
  iam_instance_profile = aws_iam_instance_profile.calcserverrole.name
  key_name             = aws_key_pair.marks_key.key_name
  force_destroy        = false

  root_block_device {
    tags = {
      "Name"       = "batchservervol"
      "billingtag" = "ukmda"
    }
    volume_size = 50
    volume_type = "gp3"
    throughput  = 125
    iops        = 3000
    encrypted   = true
    kms_key_id  = aws_kms_key.container_key.arn
  }

  tags = {
    "Name"          = "batchserver"
    "billingtag"    = "ukmda"
    "Route53FQDN"   = "batchserver.ukmeteors.co.uk"
    "DNSRecordType" = "A"
  }
  primary_network_interface {
    network_interface_id = aws_network_interface.batchserver_if.id
  }
  metadata_options {
    http_tokens = "required"
  }
}

resource "aws_network_interface" "batchserver_if" {
  subnet_id                 = aws_subnet.ec2_subnet.id
  description               = "Primary network interface"
  private_ips               = [var.batchserverip]
  security_groups           = [aws_security_group.ec2_secgrp.id]
  ipv6_address_list_enabled = false
  tags = {
    "Name"       = "batchserver"
    "billingtag" = "ukmda"
  }
}
