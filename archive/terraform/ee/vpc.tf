#
# Terraform for the VPC and networks
#

resource "aws_vpc" "default_vpc" {
  cidr_block = var.main_cidr 
  tags = {
    Name       = "default"
    billingtag = "Management"
  }
}

resource "aws_subnet" "mgmt_subnet" {
  vpc_id                  = aws_vpc.default_vpc.id
  cidr_block              = var.mgmt_cidrs 
  map_public_ip_on_launch = true
  tags = {
    Name       = "ManagementSubnet"
    billingtag = "Management"
  }
}

resource "aws_subnet" "lambda_subnet" {
  vpc_id     = aws_vpc.default_vpc.id
  cidr_block = var.lambda_cidrs
  tags = {
    Name       = "lambdaSubnet"
    billingtag = "ukmon"
  }
}

resource "aws_subnet" "ec2_subnet" {
  vpc_id                  = aws_vpc.default_vpc.id
  cidr_block              = var.ec2_cidrs
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
  default_route_table_id = aws_vpc.default_vpc.default_route_table_id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main_igw.id
  }
  tags = {
    "Name"     = "ec2_rtbl"
    billingtag = "Management"
  }
}

resource "aws_internet_gateway" "main_igw" {
  vpc_id = aws_vpc.default_vpc.id
  tags = {
    Name       = "main_igw"
    billingtag = "Management"
  }
}

