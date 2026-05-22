# Copyright (C) 2018-2023 Mark McIntyre

# SSM parameters for use in Lambdas and the batch 

resource "aws_ssm_parameter" "dev_dbhost" {
    provider = aws.eu-west-1-prov
    name  = "dev_dbhost"
  type  = "String"
  value = "3.11.55.160"
  tags = {
    "billingtag" = "ukmda"
  }
}

resource "aws_ssm_parameter" "dev_dbname" {
  provider = aws.eu-west-1-prov
  name  = "dev_dbname"
  type  = "String"
  value = "ukmon"
  tags = {
    "billingtag" = "ukmda"
  }
}

resource "aws_ssm_parameter" "dev_dbpw" {
  provider = aws.eu-west-1-prov
  name  = "dev_dbpw"
  type  = "SecureString"
  value = "Batch33mdl"
  tags = {
    "billingtag" = "ukmda"
  }
}

resource "aws_ssm_parameter" "dev_rootdbpw" {
  provider = aws.eu-west-1-prov
  name  = "dev_rootdbpw"
  type  = "SecureString"
  value = "Wombat33mdb"
  tags = {
    "billingtag" = "ukmda"
  }
}


resource "aws_ssm_parameter" "dev_dbuser" {
  provider = aws.eu-west-1-prov
  name  = "dev_dbuser"
  type  = "String"
  value = "batch"
  tags = {
    "billingtag" = "ukmda"
  }
}

resource "aws_ssm_parameter" "dev_websitebucket" {
  name  = "dev_websitebucket"
  type  = "String"
  value = var.dev_websitebucket
  tags = {
    "billingtag" = "ukmda"
  }
}

resource "aws_ssm_parameter" "dev_sharedbucket" {
  name  = "dev_sharedbucket"
  type  = "String"
  value = var.dev_sharedbucket
  tags = {
    "billingtag" = "ukmda"
  }
}

resource "aws_ssm_parameter" "dev_livebucket" {
  name  = "dev_livebucket"
  type  = "String"
  value = var.dev_livebucket
  tags = {
    "billingtag" = "ukmda"
  }
}

resource "aws_ssm_parameter" "dev_siteurl" {
  name  = "dev_siteurl"
  type  = "String"
  value = "https://www.ukmeteors.co.uk/dummy/"
  tags = {
    "billingtag" = "ukmda"
  }
}

resource "aws_ssm_parameter" "dev_envname" {
  name  = "dev_envname"
  type  = "String"
  value = "DEV"
  tags = {
    "billingtag" = "ukmda"
  }
}

resource "aws_ssm_parameter" "dev_calcinstance" {
  name  = "dev_calcinstance"
  type  = "String"
  value = "i-0ab47af23705beb31"
  tags = {
    "billingtag" = "ukmda"
  }
}
 
resource "aws_ssm_parameter" "dev_calcuser" {
  name  = "dev_calcuser"
  type  = "String"
  value = "ubuntu"
  tags = {
    "billingtag" = "ukmda"
  }
}

 
resource "aws_ssm_parameter" "dev_calcserverip" {
  name  = "dev_calcserverip"
  type  = "String"
  value = var.ubuntu_calcserverip
    tags = {
    "billingtag" = "ukmda"
  }
}

resource "aws_ssm_parameter" "dev_wmplhome" {
  name  = "dev_wmplhome"
  type  = "String"
  value = "$HOME/src/wmpldev"
  tags = {
    "billingtag" = "ukmda"
  }
}

resource "aws_ssm_parameter" "dev_rmshome" {
  name  = "dev_rmshome"
  type  = "String"
  value = "$HOME/src/RMS"
  tags = {
    "billingtag" = "ukmda"
  }
}

resource "aws_ssm_parameter" "dev_srcdir" {
  name  = "dev_srcdir"
  type  = "String"
  value = "$HOME/dev"
  tags = {
    "billingtag" = "ukmda"
  }
}

resource "aws_ssm_parameter" "dev_caminfo" {
  name  = "dev_caminfo"
  type  = "String"
  value = "$HOME/dev/data/consolidated/camera-details.csv"
  tags = {
    "billingtag" = "ukmda"
  }
}

resource "aws_ssm_parameter" "dev_sshkey" {
  name  = "dev_sshkey"
  type  = "String"
  value = "$HOME/.ssh/markskey.pem"
  tags = {
    "billingtag" = "ukmda"
  }
}

resource "aws_ssm_parameter" "dev_batchloggroup" {
  name  = "dev_batchloggroup"
  type  = "String"
  value = "/ukmondev/nightlyjob"
  tags = {
    "billingtag" = "ukmda"
  }
}

resource "aws_ssm_parameter" "dev_gmapsapikey" {
  name  = "dev_gmapsapikey"
  type  = "SecureString"
  value = "AIzaSyBFadTuzvLfkUhz8CwY2CtRDJ_lYlHUYyA"
  tags = {
    "billingtag" = "ukmda"
  }
}

# App password for ukmeteors@gmail.com
resource "aws_ssm_parameter" "dev_gmailkey" {
  name  = "dev_gmailkey"
  type  = "SecureString"
  value = "uphgxodohmfijwse"
  tags = {
    "billingtag" = "ukmda"
  }
}

