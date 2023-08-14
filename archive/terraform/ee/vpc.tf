##############################################################################
# Copyright (c) 2018- Mark McIntyre
##############################################################################
#
# Terraform for the VPC and networks
#

# the default VPC, required to exist even if not used
resource "aws_default_vpc" "default" {
  tags = {
    Name = "Default VPC"
  }
}
# default subnet, required or AWS won't create any EC2 instances
resource "aws_default_subnet" "default_subnet" {
  availability_zone = "eu-west-2a"
}

# remote VPC in the MJMM account, needed for peering
data "aws_vpc" "mjmm_ec2_vpc" {
	provider = aws.mjmmacct
	cidr_block = "172.31.0.0/16"
}

# VPC for the EC2 instances in this account
resource "aws_vpc" "ec2_vpc" {
  cidr_block = var.main_cidr
  tags = {
    Name       = "EC2VPC"
    billingtag = "Management"
  }
}

# subnet for management resources
resource "aws_subnet" "mgmt_subnet" {
  vpc_id                  = aws_vpc.ec2_vpc.id
  cidr_block              = var.mgmt_cidr
  map_public_ip_on_launch = true
  tags = {
    Name       = "ManagementSubnet"
    billingtag = "Management"
  }
}

# subnet for lambdas, if needed
resource "aws_subnet" "lambda_subnet" {
  vpc_id     = aws_vpc.ec2_vpc.id
  cidr_block = var.lambda_cidr
  tags = {
    Name       = "lambdaSubnet"
    billingtag = "ukmon"
  }
}

# subnet for EC2 instances
resource "aws_subnet" "ec2_subnet" {
  vpc_id                  = aws_vpc.ec2_vpc.id
  cidr_block              = var.ec2_cidr
  map_public_ip_on_launch = true
  tags = {
    Name       = "ec2Subnet"
    billingtag = "ukmon"
  }
}

# route table
resource "aws_default_route_table" "ec2_rtbl" {
  default_route_table_id = aws_vpc.ec2_vpc.default_route_table_id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main_igw.id
  }
  route {
    cidr_block                = data.aws_vpc.mjmm_ec2_vpc.cidr_block
    vpc_peering_connection_id = "pcx-04bcbf8428c045637"
  }
  tags = {
    "Name"     = "ec2_rtbl"
    billingtag = "Management"
  }
}

# internet gateway for this account
resource "aws_internet_gateway" "main_igw" {
  vpc_id = aws_vpc.ec2_vpc.id
  tags = {
    Name       = "main_igw"
    billingtag = "Management"
  }
}

# peering connection with the MJMM account 
resource "aws_vpc_peering_connection" "eetommpeering" {
  peer_vpc_id = data.aws_vpc.mjmm_ec2_vpc.id
  vpc_id      = aws_vpc.ec2_vpc.id
  tags = {
    "Name"       = "ee-to-mm-peering"
    "billingtag" = "ukmon"
  }
}

