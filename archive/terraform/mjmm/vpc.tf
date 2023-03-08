# Copyright (C) 2018-2023 Mark McIntyre

#
# Terraform for the VPC and networks
#

resource "aws_vpc" "main_vpc" {
  cidr_block = "172.31.0.0/16"
  tags = {
    Name       = "MainVPC"
    billingtag = "Management"
  }
}

resource "aws_subnet" "subnet1" {
  vpc_id                  = aws_vpc.main_vpc.id
  cidr_block              = "172.31.16.0/20"
  map_public_ip_on_launch = true
  tags = {
    Name       = "Subnet1"
    billingtag = "Management"
  }
}

resource "aws_subnet" "subnet2" {
  vpc_id                  = aws_vpc.main_vpc.id
  map_public_ip_on_launch = true
  cidr_block              = "172.31.32.0/20"
  tags = {
    Name       = "Subnet2"
    billingtag = "MarysWebsite"
  }
}

resource "aws_subnet" "lambdaSubnet" {
  vpc_id     = aws_vpc.main_vpc.id
  cidr_block = "172.31.255.0/28"
  tags = {
    Name       = "lambdaSubnet"
    billingtag = "ukmon"
  }
}

resource "aws_subnet" "ec2Subnet" {
  vpc_id                  = aws_vpc.main_vpc.id
  cidr_block              = "172.31.0.0/20"
  map_public_ip_on_launch = true
  tags = {
    Name       = "ec2Subnet"
    billingtag = "ukmon"
  }
}

resource "aws_route_table" "default" {
  vpc_id = aws_vpc.main_vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main_igw.id
  }
  route {
    cidr_block                = "172.32.0.0/16"
    vpc_peering_connection_id = "pcx-04bcbf8428c045637"
  }

  tags = {
    "Name"     = "default"
    billingtag = "Management"
  }
}

resource "aws_internet_gateway" "main_igw" {
  vpc_id = aws_vpc.main_vpc.id
  tags = {
    Name       = "main_igw"
    billingtag = "Management"
  }
}

# ENI attached to the spare big server
/*
resource "aws_network_interface" "mainif" {
  subnet_id   = aws_subnet.subnet2.id
  private_ips = ["172.31.34.152"]
  tags = {
    "Name"       = "UkmonHelperBigx2"
    "billingtag" = "ukmon"
    "project"    = "UKMonHelperBig"
  }
}
*/
# elastic IP attached to the ukmonhelper server
resource "aws_eip" "ukmonhelper" {
  instance = aws_instance.ukmonhelper.id
  vpc      = true
  tags = {
    billingtag = "ukmon"
  }
}

# elastic network interface attached to the ukmonhelper server
resource "aws_network_interface" "ukmon_if" {
  subnet_id                 = aws_subnet.ec2Subnet.id
  private_ips               = ["172.31.12.116"]
  security_groups           = [aws_security_group.launch-wizard-4.id]
  ipv6_address_list_enabled = false
  tags = {
    "Name"       = "ukmonhelper_if"
    "billingtag" = "ukmon"
  }
  attachment {
    instance     = aws_instance.ukmonhelper.id
    device_index = 0
  }
}

# elastic network interface attached to the calc server
/*
resource "aws_network_interface" "calcserver_if" {
  subnet_id                 = aws_subnet.ec2Subnet.id
  description               = "Primary network interface"
  private_ips               = ["172.31.12.136"]
  security_groups           = [aws_security_group.launch-wizard-4.id]
  ipv6_address_list_enabled = false
  tags = {
    "Name"       = "calcserver_if"
    "billingtag" = "ukmon"
  }
  attachment {
    instance     = aws_instance.CalcEngine4ARM.id
    device_index = 0
  }
}
*/
resource "aws_vpc_peering_connection_accepter" "eetommpeering" {
  vpc_peering_connection_id = "pcx-04bcbf8428c045637"
  tags = {
    "Name"       = "ee-to-mm-peering"
    "billingtag" = "ukmon"
  }
}
