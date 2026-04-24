# Copyright (C) 2018-2023 Mark McIntyre

# SSM parameters for use in the environment config
resource "aws_ssm_parameter" "prod_dbhost" {
    provider = aws.eu-west-1-prov
    name  = "prod_dbhost"
  type  = "String"
  value = "3.11.55.160"
  tags = {
    "billingtag" = "ukmda"
  }
}

resource "aws_ssm_parameter" "prod_dbname" {
  provider = aws.eu-west-1-prov
  name  = "prod_dbname"
  type  = "String"
  value = "ukmon"
  tags = {
    "billingtag" = "ukmda"
  }
}

resource "aws_ssm_parameter" "prod_dbpw" {
  provider = aws.eu-west-1-prov
  name  = "prod_dbpw"
  type  = "SecureString"
  value = "Batch33mdl"
  tags = {
    "billingtag" = "ukmda"
  }
}

resource "aws_ssm_parameter" "prod_dbuser" {
  provider = aws.eu-west-1-prov
  name  = "prod_dbuser"
  type  = "String"
  value = "batch"
  tags = {
    "billingtag" = "ukmda"
  }
}

resource "aws_ssm_parameter" "prod_websitebucket" {
  name  = "prod_websitebucket"
  type  = "String"
  value = var.webbucket
  tags = {
    "billingtag" = "ukmon"
  }
}

resource "aws_ssm_parameter" "prod_sharedbucket" {
  name  = "prod_sharedbucket"
  type  = "String"
  value = var.sharedbucket
  tags = {
    "billingtag" = "ukmon"
  }
}

resource "aws_ssm_parameter" "prod_livebucket" {
  name  = "prod_livebucket"
  type  = "String"
  value = var.livebucket
  tags = {
    "billingtag" = "ukmon"
  }
}

resource "aws_ssm_parameter" "prod_siteurl" {
  name  = "prod_siteurl"
  type  = "String"
  value = "https://archive.ukmeteors.co.uk" 
  tags = {
    "billingtag" = "ukmon"
  }
}

resource "aws_ssm_parameter" "prod_envname" {
  name  = "prod_envname"
  type  = "String"
  value = "PROD"
  tags = {
    "billingtag" = "ukmon"
  }
}

resource "aws_ssm_parameter" "prod_calcinstance" {
  name  = "prod_calcinstance"
  type  = "String"
  value = "i-0ab47af23705beb31"
  #value = "i-04cd701c3cfc980f5"
  tags = {
    "billingtag" = "ukmon"
  }
}
 
resource "aws_ssm_parameter" "prod_calcuser" {
  name  = "prod_calcuser"
  type  = "String"
  value = "ubuntu"
  #value = "ec2-user" # "ubuntu"
  tags = {
    "billingtag" = "ukmon"
  }
}
 
resource "aws_ssm_parameter" "prod_calcip" {
  name  = "prod_calcserverip"
  type  = "String"
  value = "172.32.16.137"
    tags = {
    "billingtag" = "ukmon"
  }
}
resource "aws_ssm_parameter" "prod_backupinstance" {
  name  = "prod_backupinstance"
  type  = "String"
  value = "i-081af8754587bc7fa"
  tags = {
    "billingtag" = "ukmon"
  }
}
 
resource "aws_ssm_parameter" "prod_wmplhome" {
  name  = "prod_wmplhome"
  type  = "String"
  value = "/home/ec2-user/src/WesternMeteorPyLib"
  tags = {
    "billingtag" = "ukmon"
  }
}

resource "aws_ssm_parameter" "prod_rmshome" {
  name  = "prod_rmshome"
  type  = "String"
  value = "/home/ec2-user/src/RMS"
  tags = {
    "billingtag" = "ukmon"
  }
}

resource "aws_ssm_parameter" "prod_srcdir" {
  name  = "prod_srcdir"
  type  = "String"
  value = "/home/ec2-user/prod"
  tags = {
    "billingtag" = "ukmon"
  }
}

resource "aws_ssm_parameter" "prod_caminfo" {
  name  = "prod_caminfo"
  type  = "String"
  value = "/home/ec2-user/prod/data/consolidated/camera-details.csv"
  tags = {
    "billingtag" = "ukmon"
  }
}

resource "aws_ssm_parameter" "prod_sshkey" {
  name  = "prod_sshkey"
  type  = "String"
  value = "/home/ec2-user/.ssh/markskey.pem"
  tags = {
    "billingtag" = "ukmon"
  }
}

resource "aws_ssm_parameter" "prod_batchloggroup" {
  name  = "prod_batchloggroup"
  type  = "String"
  value = "/ukmonbatch/nightlyjob"
  tags = {
    "billingtag" = "ukmon"
  }
}
