# Copyright (C) 2018-2023 Mark McIntyre

# SSM parameters for use in Lambdas and the batch 

resource "aws_ssm_parameter" "prod_dbhost" {
    provider = aws.eu-west-1-prov
    name  = "prod_dbhost"
  type  = "String"
  value = "batchserver.ukmeteors.co.uk"
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

resource "aws_ssm_parameter" "prod_rootdbpw" {
  provider = aws.eu-west-1-prov
  name  = "prod_rootdbpw"
  type  = "SecureString"
  value = "Wombat33mdb"
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
  value = var.websitebucket
  tags = {
    "billingtag" = "ukmda"
  }
}

resource "aws_ssm_parameter" "prod_sharedbucket" {
  name  = "prod_sharedbucket"
  type  = "String"
  value = var.sharedbucket
  tags = {
    "billingtag" = "ukmda"
  }
}

resource "aws_ssm_parameter" "prod_livebucket" {
  name  = "prod_livebucket"
  type  = "String"
  value = var.livebucket
  tags = {
    "billingtag" = "ukmda"
  }
}

resource "aws_ssm_parameter" "prod_siteurl" {
  name  = "prod_siteurl"
  type  = "String"
  value = "https://archive.ukmeteors.co.uk" 
  tags = {
    "billingtag" = "ukmda"
  }
}

resource "aws_ssm_parameter" "prod_envname" {
  name  = "prod_envname"
  type  = "String"
  value = "PROD"
  tags = {
    "billingtag" = "ukmda"
  }
}

resource "aws_ssm_parameter" "prod_calcinstance" {
  name  = "prod_calcinstance"
  type  = "String"
  value = "i-0ab47af23705beb31"
  tags = {
    "billingtag" = "ukmda"
  }
}
 
resource "aws_ssm_parameter" "prod_calcuser" {
  name  = "prod_calcuser"
  type  = "String"
  value = "ubuntu"
  tags = {
    "billingtag" = "ukmda"
  }
}

 
resource "aws_ssm_parameter" "prod_calcserverip" {
  name  = "prod_calcserverip"
  type  = "String"
  value = var.ubuntu_calcserverip
    tags = {
    "billingtag" = "ukmda"
  }
}

resource "aws_ssm_parameter" "prod_wmplhome" {
  name  = "prod_wmplhome"
  type  = "String"
  value = "$HOME/src/WesternMeteorPyLib"
  tags = {
    "billingtag" = "ukmda"
  }
}

resource "aws_ssm_parameter" "prod_rmshome" {
  name  = "prod_rmshome"
  type  = "String"
  value = "$HOME/src/RMS"
  tags = {
    "billingtag" = "ukmda"
  }
}

resource "aws_ssm_parameter" "prod_srcdir" {
  name  = "prod_srcdir"
  type  = "String"
  value = "$HOME/prod"
  tags = {
    "billingtag" = "ukmda"
  }
}

resource "aws_ssm_parameter" "prod_caminfo" {
  name  = "prod_caminfo"
  type  = "String"
  value = "$HOME/prod/data/consolidated/camera-details.csv"
  tags = {
    "billingtag" = "ukmda"
  }
}

resource "aws_ssm_parameter" "prod_sshkey" {
  name  = "prod_sshkey"
  type  = "String"
  value = "$HOME/.ssh/markskey.pem"
  tags = {
    "billingtag" = "ukmda"
  }
}

resource "aws_ssm_parameter" "prod_batchloggroup" {
  name  = "prod_batchloggroup"
  type  = "String"
  value = "/ukmonbatch/nightlyjob"
  tags = {
    "billingtag" = "ukmda"
  }
}

resource "aws_ssm_parameter" "prod_gmapsapikey" {
  name  = "prod_gmapsapikey"
  type  = "SecureString"
  value = "AIzaSyBFadTuzvLfkUhz8CwY2CtRDJ_lYlHUYyA"
  tags = {
    "billingtag" = "ukmda"
  }
}

