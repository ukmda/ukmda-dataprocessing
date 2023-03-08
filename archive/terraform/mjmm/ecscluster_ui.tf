# Copyright (C) 2018-2023 Mark McIntyre

# terraform to create ECS cluster for the UI

# some variables for the cluster and task defns
variable "ui_ecsloggroup" { default = "/ecs/simpleui" }
variable "ui_containername" { default = "simpleui" }

# create a cluster
resource "aws_ecs_cluster" "ui_cluster" {
  name = var.ui_containername
  tags = {
    "billingtag" = "mjmm"
  }
}

# declare the capacity provider type, in this case FARGATE
resource "aws_ecs_cluster_capacity_providers" "ui_cluster_cap" {
  cluster_name       = aws_ecs_cluster.ui_cluster.name
  capacity_providers = ["FARGATE", "FARGATE_SPOT"]
}

data "template_file" "ui_task_json_template" {
  template = file("files/${var.ui_containername}/${var.ui_containername}_container.json")
  vars = {
    acctid   = data.aws_caller_identity.current.account_id
    regionid = "eu-west-2"
    repoid   = "ukmon/${var.ui_containername}"
    contname = var.ui_containername
    loggrp   = var.ui_ecsloggroup
  }
}

# define the task
# the definition of the container it runs are in the webapp.json file
resource "aws_ecs_task_definition" "simpleui_task" {
  family                = var.ui_containername
  container_definitions = data.template_file.ui_task_json_template.rendered
  cpu                   = 4096
  memory                = 8192
  network_mode          = "awsvpc"
  tags = {
    billingtag = "mjmm"
  }
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = aws_iam_role.ui_ecstaskrole.arn 
  task_role_arn            = aws_iam_role.ui_ecstaskrole.arn 
  runtime_platform {
    operating_system_family = "LINUX"
  }
}

# define a service to run the task
resource "aws_ecs_service" "ui_service" {
  name                    = var.ui_containername
  cluster                 = aws_ecs_cluster.ui_cluster.id
  task_definition         = aws_ecs_task_definition.simpleui_task.arn
  desired_count           = 0
  enable_ecs_managed_tags = true
  wait_for_steady_state   = false
  launch_type             = "FARGATE"
  network_configuration {
    assign_public_ip = true
    security_groups = [
      aws_security_group.ui_secgrp.id
    ]
    subnets = [
      aws_subnet.ecs_subnet.id
    ]
  }
}

# iam role for the task to use
resource "aws_iam_role" "ui_ecstaskrole" {
  name               = "ecsTaskExecutionRoleForUI"
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
    },
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

# iam policies to attach to iam role 
resource "aws_iam_role_policy_attachment" "ui_ecspolicy" {
  role       = aws_iam_role.ui_ecstaskrole.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy" "ui_container_logging_policy" {
  name   = "containerLoggingPolForUI"
  role   = aws_iam_role.ui_ecstaskrole.name
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

resource "aws_iam_role_policy_attachment" "ui_xacctaccessecs" {
  role       = aws_iam_role.ui_ecstaskrole.name
  policy_arn = aws_iam_policy.ui_crossacctpolicyecs.arn
}

resource "aws_iam_policy" "ui_crossacctpolicyecs" {
  name = "CrossAcctPolForUI"
  policy = jsonencode(
    {
      Statement = [
        {
          Action = [
            "sts:AssumeRole",
          ]
          Effect = "Allow"
          Resource = [
            "arn:aws:iam::822069317839:role/service-role/S3FullAccess",
          ]
        },
      ]
      Version = "2012-10-17"
    }
  )
  tags = {
    "billingtag" = "mjmm"
  }
}

# security group for the service to use
resource "aws_security_group" "ui_secgrp" {
  name        = "secGrpForUI"
  description = "Security Group for UI ECS Fargate"
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
    },
    {
      description      = ""
      from_port        = 80
      to_port          = 80
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
    billingtag = "mjmm"
  }
}

# print out some results - clustername, sec grp, subnet and role arn
output "ui_clusname" { value = aws_ecs_cluster.ui_cluster.name }
output "ui_contname" { value = var.ui_containername }
