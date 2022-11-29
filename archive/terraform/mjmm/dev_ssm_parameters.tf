# SSM parameters for use in the environment config

resource "aws_ssm_parameter" "dev_websitebucket" {
  name  = "dev_websitebucket"
  type  = "String"
  value = "mjmm-ukmonarchive.co.uk" 
  tags = {
    "billingtag" = "ukmon"
  }
}

resource "aws_ssm_parameter" "dev_sharedbucket" {
  name  = "dev_sharedbucket"
  type  = "String"
  value = "ukmon-shared"
  tags = {
    "billingtag" = "ukmon"
  }
}

resource "aws_ssm_parameter" "dev_livebucket" {
  name  = "dev_livebucket"
  type  = "String"
  value = "mjmm-live"
  tags = {
    "billingtag" = "ukmon"
  }
}

resource "aws_ssm_parameter" "dev_siteurl" {
  name  = "dev_siteurl"
  type  = "String"
  value = "http://mjmm-ukmonarchive.co.uk.s3-website.eu-west-2.amazonaws.com"
  tags = {
    "billingtag" = "ukmon"
  }
}

resource "aws_ssm_parameter" "dev_envname" {
  name  = "dev_envname"
  type  = "String"
  value = "DEV"
  tags = {
    "billingtag" = "ukmon"
  }
}

resource "aws_ssm_parameter" "dev_calcinstance" {
  name  = "dev_calcinstance"
  type  = "String"
  value = "i-0da38ed8aea1a1d85"
  tags = {
    "billingtag" = "ukmon"
  }
}
 
resource "aws_ssm_parameter" "dev_backupinstance" {
  name  = "dev_backupinstance"
  type  = "String"
  value = "i-081af8754587bc7fa"
  tags = {
    "billingtag" = "ukmon"
  }
}
 
resource "aws_ssm_parameter" "dev_wmplhome" {
  name  = "dev_wmplhome"
  type  = "String"
  value = "/home/ec2-user/src/wmpldev"
  tags = {
    "billingtag" = "ukmon"
  }
}

resource "aws_ssm_parameter" "dev_rmshome" {
  name  = "dev_rmshome"
  type  = "String"
  value = "/home/ec2-user/src/RMS"
  tags = {
    "billingtag" = "ukmon"
  }
}

resource "aws_ssm_parameter" "dev_srcdir" {
  name  = "dev_srcdir"
  type  = "String"
  value = "/home/ec2-user/dev"
  tags = {
    "billingtag" = "ukmon"
  }
}

resource "aws_ssm_parameter" "dev_caminfo" {
  name  = "dev_caminfo"
  type  = "String"
  value = "/home/ec2-user/dev/data/consolidated/camera-details.csv"
  tags = {
    "billingtag" = "ukmon"
  }
}

resource "aws_ssm_parameter" "dev_sshkey" {
  name  = "dev_sshkey"
  type  = "String"
  value = "/home/ec2-user/.ssh/markskey.pem"
  tags = {
    "billingtag" = "ukmon"
  }
}
