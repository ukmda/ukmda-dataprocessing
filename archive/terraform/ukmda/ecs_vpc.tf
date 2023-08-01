#
# Create a VPC for the use of ECS and possibly other assets
# Copyright (C) 2018-2023 Mark McIntyre
#
#data used by the code in several places
data "aws_region" "current" {}

# some variables for the cluster and task defns
variable "ecsloggroup" { default = "/ecs/trajcont" }
variable "containername" { default = "trajcont" }

# create a VPC for the cluster
resource "aws_vpc" "ecs_vpc" {
  cidr_block = "172.128.0.0/16"
  tags = {
    Name         = "ecsVPC"
    "billingtag" = "ukmon"
  }
}
# create a subnet for the cluster
resource "aws_subnet" "ecs_subnet" {
  vpc_id                  = aws_vpc.ecs_vpc.id
  cidr_block              = "172.128.16.0/20"
  map_public_ip_on_launch = true
  tags = {
    Name         = "ecs_subnet"
    "billingtag" = "ukmon"
  }
}

resource "aws_internet_gateway" "ecs_igw" {
  vpc_id = aws_vpc.ecs_vpc.id

  tags = {
    Name         = "ecs_igw"
    "billingtag" = "ukmon"
  }
}

# route table that directs traffic to the IGW
resource "aws_default_route_table" "ecs_default_rtbl" {
  default_route_table_id = aws_vpc.ecs_vpc.default_route_table_id
  route {
    cidr_block = "0.0.0.0/0"
    #gateway_id = "igw-8cc667e5"
    gateway_id = aws_internet_gateway.ecs_igw.id
  }
  tags = {
    Name         = "ecs_def_route"
    "billingtag" = "ukmon"
  }
}
