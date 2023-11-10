# Copyright (C) 2018-2023 Mark McIntyre

#
# Terraform for the VPC and networks
#

resource "aws_vpc" "main_vpc" {
  cidr_block                        = "172.31.0.0/16"
  assign_generated_ipv6_cidr_block  = true
  tags = {
    Name       = "MainVPC"
    billingtag = "Management"
  }
}

resource "aws_subnet" "subnet1" {
  vpc_id                  = aws_vpc.main_vpc.id
  cidr_block              = "172.31.16.0/20"
  ipv6_cidr_block         = "2a05:d01c:a00:3200::/64"
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
    ipv6_cidr_block = "::/48"
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

resource "aws_vpc_peering_connection_accepter" "eetommpeering" {
  vpc_peering_connection_id = "pcx-04bcbf8428c045637"
  tags = {
    "Name"       = "ee-to-mm-peering"
    "billingtag" = "ukmon"
  }
}

resource "aws_vpc_peering_connection_accepter" "mdatommpeering" {
  vpc_peering_connection_id = "pcx-0beef413172ec795e"
  tags = {
    "Name"       = "ukmda-to-mm-peering"
    "billingtag" = "ukmda"
  }
}
