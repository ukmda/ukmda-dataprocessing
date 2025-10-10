# Copyright (C) 2018-2023 Mark McIntyre

# SSM parameters for use in Lambdas

resource "aws_ssm_parameter" "prod_dbhost" {
    provider = aws.eu-west-1-prov
    name  = "prod_dbhost"
  type  = "String"
  value = "3.11.55.160"
  tags = {
    "billingtag" = "ukmon"
  }
}

resource "aws_ssm_parameter" "prod_dbname" {
  provider = aws.eu-west-1-prov
  name  = "prod_dbname"
  type  = "String"
  value = "ukmon"
  tags = {
    "billingtag" = "ukmon"
  }
}

resource "aws_ssm_parameter" "prod_dbpw" {
  provider = aws.eu-west-1-prov
  name  = "prod_dbpw"
  type  = "SecureString"
  value = "Batch33mdl"
  tags = {
    "billingtag" = "ukmon"
  }
}

resource "aws_ssm_parameter" "prod_dbuser" {
  provider = aws.eu-west-1-prov
  name  = "prod_dbuser"
  type  = "String"
  value = "batch"
  tags = {
    "billingtag" = "ukmon"
  }
}
