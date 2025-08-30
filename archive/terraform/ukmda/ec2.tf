# Copyright (C) 2018-2023 Mark McIntyre

resource "aws_instance" "calc_server" {
  ami                  = "ami-0df2d8f6def0bd716"
  instance_type        = "c8g.4xlarge"
  iam_instance_profile = aws_iam_instance_profile.calcserverrole.name
  key_name             = aws_key_pair.marks_key.key_name
  force_destroy        = false
  tags = {
    "Name"          = "Calcengine"
    "billingtag"    = "ukmda"
    "Route53FQDN"   = "calcengine.ukmeteors.co.uk"
    "DNSRecordType" = "A"
  }
  root_block_device {
    tags = {
      "Name"       = "calcengine"
      "billingtag" = "ukmda"
    }
    volume_size = 100
  }
  primary_network_interface {
    network_interface_id = aws_network_interface.calcserver_if.id
  }

  metadata_options {
    http_tokens = "required"
  }
}

# elastic network interface attached to the calc server

resource "aws_network_interface" "calcserver_if" {
  subnet_id                 = aws_subnet.ec2_subnet.id
  description               = "Primary network interface"
  private_ips               = [var.calcserverip]
  security_groups           = [aws_security_group.ec2_secgrp.id]
  ipv6_address_list_enabled = false
  tags = {
    "Name"       = "calcengine"
    "billingtag" = "ukmda"
  }
}
################################################
#  Ubuntu calc server
################################################

resource "aws_instance" "ubuntu_calc_server" {
  ami                  = "ami-0bdf149a42243bde8"
  instance_type        = "c6g.4xlarge"
  iam_instance_profile = aws_iam_instance_profile.calcserverrole.name
  key_name             = aws_key_pair.marks_key.key_name
  tags = {
    "Name"          = "calcengine_ub"
    "billingtag"    = "ukmda"
    "Route53FQDN"   = "calcengine_ub.ukmeteors.co.uk"
    "DNSRecordType" = "A"
  }
  root_block_device {
    tags = {
      "Name"       = "calcengine2"
      "billingtag" = "ukmda"
    }
    volume_size = 100
  }
  primary_network_interface {
    network_interface_id = aws_network_interface.ubuntu_calcserver_if.id
  }
  metadata_options {
    http_tokens = "required"
  }
}

# elastic network interface attached to the calc server

resource "aws_network_interface" "ubuntu_calcserver_if" {
  subnet_id                 = aws_subnet.ec2_subnet.id
  description               = "Primary network interface"
  private_ips               = [var.ubuntu_calcserverip]
  security_groups           = [aws_security_group.ec2_secgrp.id]
  ipv6_address_list_enabled = false
  tags = {
    "Name"       = "calcengine2"
    "billingtag" = "ukmda"
  }
}

################################################
#  admin server
################################################


resource "aws_instance" "admin_server" {
  ami                  = "ami-0c1ce90bf42d9802b"
  instance_type        = "t2.micro"
  iam_instance_profile = aws_iam_instance_profile.S3FullAccess.name
  key_name             = aws_key_pair.marks_key.key_name
  tags = {
    "Name"          = "AdminServer"
    "billingtag"    = "ukmda"
    "Route53FQDN"   = "adminserver.ukmeteors.co.uk"
    "DNSRecordType" = "A"
  }
  root_block_device {
    tags = {
      "Name"       = "adminserver"
      "billingtag" = "ukmda"
    }
    volume_size = 8
  }
  metadata_options {
    http_tokens = "required"
  }

}
