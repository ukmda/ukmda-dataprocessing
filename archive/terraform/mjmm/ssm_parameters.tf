# SSM parameters for use in the environment config

resource "aws_ssm_parameter" "prod_websitebucket" {
  name  = "prod_websitebucket"
  type  = "String"
  value = "ukmeteornetworkarchive" 
  tags = {
    "billingtag" = "ukmon"
  }
}

resource "aws_ssm_parameter" "prod_sharedbucket" {
  name  = "prod_sharedbucket"
  type  = "String"
  value = "ukmon-shared"
  tags = {
    "billingtag" = "ukmon"
  }
}

resource "aws_ssm_parameter" "prod_livebucket" {
  name  = "prod_livebucket"
  type  = "String"
  value = "ukmon-live"
  tags = {
    "billingtag" = "ukmon"
  }
}

resource "aws_ssm_parameter" "prod_siteurl" {
  name  = "prod_siteurl"
  type  = "String"
  value = "https://archive.ukmeteornetwork.co.uk"
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
  value = "i-0da38ed8aea1a1d85"
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

resource "aws_ssm_parameter" "prod_archdir" {
  name  = "prod_archdir"
  type  = "String"
  value = "/home/ec2-user/ukmon-shared/archive"
  tags = {
    "billingtag" = "ukmon"
  }
}

resource "aws_ssm_parameter" "prod_matchdir" {
  name  = "prod_matchdir"
  type  = "String"
  value = "/home/ec2-user/ukmon-shared/matches"
  tags = {
    "billingtag" = "ukmon"
  }
}

resource "aws_ssm_parameter" "prod_caminfo" {
  name  = "prod_caminfo"
  type  = "String"
  value = "/home/ec2-user/ukmon-shared/consolidated/camera-details.csv"
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
