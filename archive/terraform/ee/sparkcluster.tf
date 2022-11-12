#
# create a cluster for Spark
#

# some variables for the cluster and task defns
variable "sparkloggroup" { default = "/ecs/sparkcont" }
variable "sparkcontainername" { default = "sparkcont" }

# create an ECS cluster
resource "aws_ecs_cluster" "sparkcluster" {
  name = "sparkcluster"
  tags = {
    "billingtag" = "ukmon"
  }
}

# declare the capacity provider type, in this case FARGATE
resource "aws_ecs_cluster_capacity_providers" "sparkcluster_cap" {
  cluster_name       = aws_ecs_cluster.sparkcluster.name
  capacity_providers = ["FARGATE", "FARGATE_SPOT"]
  depends_on = [ aws_iam_role.sparktaskrole ]
}

# Task template file
data "template_file" "spark_task_json_template" {
  template = file("files/sparkcluster/spark_container.json")
  vars = {
    acctid   = data.aws_caller_identity.current.account_id
    regionid = "eu-west-2"
    repoid   = "ukmon/datachefspark"
    contname = var.sparkcontainername
    loggrp   = var.sparkloggroup
  }
}

# define the task
# the definition of the container it runs are in the webapp.json file
resource "aws_ecs_task_definition" "spark_task" {
  family                = "spark"
  container_definitions = data.template_file.spark_task_json_template.rendered
  cpu                   = 512
  memory                = 2048
  network_mode          = "awsvpc"
  tags = {
    billingtag = "ukmon"
  }
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = aws_iam_role.sparktaskrole.arn 
  task_role_arn            = aws_iam_role.sparktaskrole.arn 
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
resource "aws_iam_role" "sparktaskrole" {
  name               = "sparkTaskExecutionRole"
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
resource "aws_iam_role_policy_attachment" "sparkpolicy1" {
  role       = aws_iam_role.sparktaskrole.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy" "spark_container_logging_policy" {
  name   = "spark_container_logging_policy"
  role   = aws_iam_role.sparktaskrole.name
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
resource "aws_security_group" "sparksecgrp" {
  name        = "spark-secgrp"
  description = "Security Group for Spark on Fargate"
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

