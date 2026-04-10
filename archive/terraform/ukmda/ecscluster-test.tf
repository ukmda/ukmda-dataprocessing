# terraform to create ECS cluster
# Copyright (C) 2018-2023 Mark McIntyre

variable "ecsloggrouptest" { default = "/ecs/trajcontest" }
variable "containernametest" { default = "trajconttest" }

# create a cluster
resource "aws_ecs_cluster" "trajsolvertest" {
  name = "trajsolvertest"
  tags = {
    "billingtag" = "ukmda"
  }
}

# declare the capacity provider type, in this case FARGATE
resource "aws_ecs_cluster_capacity_providers" "trajsolvertest_cap" {
  cluster_name       = aws_ecs_cluster.trajsolvertest.name
  capacity_providers = ["FARGATE", "FARGATE_SPOT"]
}

data "template_file" "tasktest_json_template" {
  template = file("files/trajsolver/trajsolver_container.json")
  vars = {
    acctid   = data.aws_caller_identity.current.account_id
    regionid = "eu-west-2"
    repoid   = "calcengine/trajsolvertest"
    contname = var.containernametest
    loggrp   = var.ecsloggrouptest
  }
}

# define the task
# the definition of the container it runs are in the webapp.json file
resource "aws_ecs_task_definition" "trajsolvertest_task" {
  family                = "trajsolvertest"
  container_definitions = data.template_file.tasktest_json_template.rendered
  cpu                   = 4096
  memory                = 8192
  network_mode          = "awsvpc"
  tags = {
    billingtag = "ukmda"
  }
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = aws_iam_role.ecstaskrole.arn 
  task_role_arn            = aws_iam_role.ecstaskrole.arn 
  runtime_platform {
    operating_system_family = "LINUX"
  }
}

/*
# print out some results - clustername, sec grp, subnet and role arn
output "clusname" { value = aws_ecs_cluster.trajsolver.name }
output "secgrpid" { value = aws_security_group.ecssecgrp.id }
output "subnetid" { value = aws_subnet.ecs_subnet.id }
output "taskrolearn" { value = aws_iam_role.ecstaskrole.arn }
output "loggrp" { value = var.ecsloggroup }
output "contname" { value = var.containername }
*/
# create a local file containing the clustername and a few other details
#
resource "null_resource" "createECSdetailstest" {
  triggers = {
    clusname = join(",", tolist([aws_ecs_cluster.trajsolvertest.name,
      aws_subnet.ecs_subnet.id,
      aws_security_group.ecssecgrp.id,
    aws_iam_role.ecstaskrole.arn, var.ecsloggroup,
    var.containername]))
  }
  provisioner "local-exec" {
    command     = "echo $env:CLUSNAME $env:SECGRP $env:SUBNET $env:IAMROLE $env:LOGGRP $env:CONTNAME > ../../ukmon_pylib/traj/clusdetailstest-ukmda.txt"
    interpreter = ["pwsh.exe", "-command"]
    environment = {
      CLUSNAME = "${aws_ecs_cluster.trajsolvertest.name}"
      SECGRP   = "${aws_security_group.ecssecgrp.id}"
      SUBNET   = "${aws_subnet.ecs_subnet.id}"
      IAMROLE  = "${aws_iam_role.ecstaskrole.arn}"
      LOGGRP   = "${var.ecsloggrouptest}"
      CONTNAME = "${var.containername}"
    }
  }
}
