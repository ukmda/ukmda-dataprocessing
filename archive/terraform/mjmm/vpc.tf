#
# Terraform for the VPC and networks
#

resource "aws_vpc" "main_vpc" {
  cidr_block = "172.31.0.0/16"
}

resource "aws_subnet" "subnet1" {
  vpc_id                  = aws_vpc.main_vpc.id
  cidr_block              = "172.31.16.0/20"
  map_public_ip_on_launch = true
  tags = {
    Name = "Subnet1"
  }
}

resource "aws_subnet" "subnet2" {
  vpc_id                  = aws_vpc.main_vpc.id
  map_public_ip_on_launch = true
  cidr_block              = "172.31.32.0/20"
  tags = {
    Name = "Subnet2"
  }
}

resource "aws_subnet" "lambdaSubnet" {
  vpc_id     = aws_vpc.main_vpc.id
  cidr_block = "172.31.255.0/28"
  tags = {
    Name = "lambdaSubnet"
  }
}

resource "aws_subnet" "ec2Subnet" {
  vpc_id                  = aws_vpc.main_vpc.id
  cidr_block              = "172.31.0.0/20"
  map_public_ip_on_launch = true
  tags = {
    Name = "ec2Subnet"
  }
}

resource "aws_route_table" "default" {
  vpc_id = aws_vpc.main_vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main_igw.id
  }
  tags = {
    "Name" = "default"
  }
}

resource "aws_route_table" "lambda_to_internet" {
  vpc_id = aws_vpc.main_vpc.id
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = "nat-0e203492f202148f1"
  }
  tags = {
    "Name" = "lambda_to_internet"
  }
}

resource "aws_internet_gateway" "main_igw" {
  vpc_id = aws_vpc.main_vpc.id
  tags = {
    Name = "main_igw"
  }
}

resource "aws_network_interface" "mainif" {
  subnet_id   = aws_subnet.subnet2.id
  private_ips = ["172.31.34.152"]
  tags = {
    "Name"       = "UkmonHelperBigx2"
    "billingtag" = "ukmon"
    "project"    = "UKMonHelperBig"
  }
}

resource "aws_eip" "lambdaeip" {
  network_interface = "eni-0cecdd958c8f43ef7"
  #associate_with_private_ip = "172.31.0.102"
  vpc = true
}

resource "aws_eip" "ukmonhelper" {
  instance = aws_instance.ukmonhelper.id
  vpc      = true
}

resource "aws_nat_gateway" "lambdaNatGW" {
  allocation_id = aws_eip.lambdaeip.id
  subnet_id     = aws_subnet.ec2Subnet.id
  tags = {
    Name = "lambdaNatGW"
  }
  # To ensure proper ordering, it is recommended to add an explicit dependency
  # on the Internet Gateway for the VPC.
  depends_on = [aws_internet_gateway.main_igw]
}