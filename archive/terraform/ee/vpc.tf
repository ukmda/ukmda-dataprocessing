#
# Terraform for the VPC and networks
#

resource "aws_default_vpc" "default" {
  tags = {
    Name = "Default VPC"
  }
}
resource "aws_vpc" "ec2_vpc" {
  cidr_block = var.main_cidr
  tags = {
    Name       = "EC2VPC"
    billingtag = "Management"
  }
}

resource "aws_subnet" "mgmt_subnet" {
  vpc_id                  = aws_vpc.ec2_vpc.id
  cidr_block              = var.mgmt_cidr
  map_public_ip_on_launch = true
  tags = {
    Name       = "ManagementSubnet"
    billingtag = "Management"
  }
}

resource "aws_subnet" "lambda_subnet" {
  vpc_id     = aws_vpc.ec2_vpc.id
  cidr_block = var.lambda_cidr
  tags = {
    Name       = "lambdaSubnet"
    billingtag = "ukmon"
  }
}

resource "aws_subnet" "ec2_subnet" {
  vpc_id                  = aws_vpc.ec2_vpc.id
  cidr_block              = var.ec2_cidr
  map_public_ip_on_launch = true
  tags = {
    Name       = "ec2Subnet"
    billingtag = "ukmon"
  }
}

resource "aws_default_subnet" "default_subnet" {
  availability_zone = "eu-west-2a"
}

resource "aws_default_route_table" "ec2_rtbl" {
  default_route_table_id = aws_vpc.ec2_vpc.default_route_table_id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main_igw.id
  }
  route {
    cidr_block                = "172.31.0.0/16"
    vpc_peering_connection_id = "pcx-04bcbf8428c045637"
  }
  tags = {
    "Name"     = "ec2_rtbl"
    billingtag = "Management"
  }
}

resource "aws_internet_gateway" "main_igw" {
  vpc_id = aws_vpc.ec2_vpc.id
  tags = {
    Name       = "main_igw"
    billingtag = "Management"
  }
}

resource "aws_vpc_peering_connection" "eetommpeering" {
  peer_vpc_id = "vpc-a19015c8"
  vpc_id      = aws_vpc.ec2_vpc.id
  tags = {
    "Name"       = "ee-to-mm-peering"
    "billingtag" = "ukmon"
  }
}

