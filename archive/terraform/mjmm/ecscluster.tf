# terraform to create ECS cluster

#data used by the code in several places
data "aws_region" "current" {}
data "aws_caller_identity" "current" {}

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

# create a cluster
resource "aws_ecs_cluster" "trajsolver" {
  name = "trajsolver"
  tags = {
    "billingtag" = "ukmon"
  }
}

# declare the capacity provider type, in this case FARGATE
resource "aws_ecs_cluster_capacity_providers" "trajsolver_cap" {
  cluster_name       = aws_ecs_cluster.trajsolver.name
  capacity_providers = ["FARGATE", "FARGATE_SPOT"]
}

data "template_file" "task_json_template" {
  template = file("trajsolver_container.json")
  vars = {
    acctid   = data.aws_caller_identity.current.account_id
    regionid = "eu-west-2"
    repoid   = "ukmon/trajsolver"
    contname = var.containername
    loggrp   = var.ecsloggroup
  }
}

# define the task
# the definition of the container it runs are in the webapp.json file
resource "aws_ecs_task_definition" "trajsolver_task" {
  family                = "trajsolver"
  container_definitions = data.template_file.task_json_template.rendered
  cpu                   = 4096
  memory                = 8192
  network_mode          = "awsvpc"
  tags = {
    billingtag = "ukmon"
  }
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/ecsTaskExecutionRole"
  task_role_arn            = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/ecsTaskExecutionRole"
  runtime_platform {
    operating_system_family = "LINUX"
  }
}

# define a service to run the task
#resource "aws_ecs_service" "trajsolver_service" {
#  name                    = "trajsolver"
#  cluster                 = aws_ecs_cluster.trajsolver.id
#  task_definition         = aws_ecs_task_definition.trajsolver_task.arn
#  desired_count           = 0
#  enable_ecs_managed_tags = true
#  wait_for_steady_state   = false
#  launch_type             = "FARGATE"
#  network_configuration {
#    assign_public_ip = true
#    security_groups = [
#      aws_security_group.ecssecgrp.id
#    ]
#    subnets = [
#      aws_subnet.ecs_subnet.id
#    ]
#  }
#}

# iam role for the task to use
resource "aws_iam_role" "ecstaskrole" {
  name               = "ecsTaskExecutionRole"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

# iam policies to attach to iam role 
resource "aws_iam_role_policy_attachment" "ecspolicy1" {
  role       = aws_iam_role.ecstaskrole.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy" "container_logging_policy" {
  name   = "container_logging_policy"
  role   = aws_iam_role.ecstaskrole.name
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
        "Effect": "Allow",
        "Action": [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents"
        ],
        "Resource": "*"
    }
  ]
}
EOF
}


# security group for the service to use
resource "aws_security_group" "ecssecgrp" {
  name        = "ecs-secgrp"
  description = "Security Group for ECS Fargate"
  vpc_id      = aws_vpc.ecs_vpc.id
  ingress = [
    {
      description      = ""
      from_port        = 22
      to_port          = 22
      protocol         = "tcp"
      cidr_blocks      = ["0.0.0.0/0"]
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      security_groups  = []
      self             = false
    }
  ]
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    billingtag = "ukmon"
  }
}

# print out some results - clustername, sec grp, subnet and role arn
output "clusname" { value = aws_ecs_cluster.trajsolver.name }
output "secgrpid" { value = aws_security_group.ecssecgrp.id }
output "subnetid" { value = aws_subnet.ecs_subnet.id }
output "taskrolearn" { value = aws_iam_role.ecstaskrole.arn }
output "loggrp" { value = var.ecsloggroup }
output "contname" { value = var.containername }
# create a local file containing the clustername and a few other details
#
resource "null_resource" "createECSdetails" {
  triggers = {
    clusname = join(",", tolist([aws_ecs_cluster.trajsolver.name,
      aws_subnet.ecs_subnet.id,
      aws_security_group.ecssecgrp.id,
    aws_iam_role.ecstaskrole.arn, var.ecsloggroup,
    var.containername]))
  }
  provisioner "local-exec" {
    command     = "echo $env:CLUSNAME $env:SECGRP $env:SUBNET $env:IAMROLE $env:LOGGRP $env:CONTNAME > ../../../ukmon_pylib/traj/clusdetails.txt"
    interpreter = ["pwsh.exe", "-command"]
    environment = {
      CLUSNAME = "${aws_ecs_cluster.trajsolver.name}"
      SECGRP   = "${aws_security_group.ecssecgrp.id}"
      SUBNET   = "${aws_subnet.ecs_subnet.id}"
      IAMROLE  = "${aws_iam_role.ecstaskrole.arn}"
      LOGGRP   = "${var.ecsloggroup}"
      CONTNAME = "${var.containername}"
    }
  }
}
