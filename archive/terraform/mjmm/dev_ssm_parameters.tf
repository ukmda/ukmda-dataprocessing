# SSM parameters for use in the environment config

resource "aws_ssm_parameter" "dev_websitebucket" {
  name  = "dev_websitebucket"
  type  = "String"
  value = "mjmm-ukmonarchive.co.uk" 
}

resource "aws_ssm_parameter" "dev_sharedbucket" {
  name  = "dev_sharedbucket"
  type  = "String"
  value = "ukmon-shared"
}

resource "aws_ssm_parameter" "dev_livebucket" {
  name  = "dev_livebucket"
  type  = "String"
  value = "mjmm-live"
}

resource "aws_ssm_parameter" "dev_siteurl" {
  name  = "dev_siteurl"
  type  = "String"
  value = "http://mjmm-ukmonarchive.co.uk.s3-website.eu-west-2.amazonaws.com"
}

resource "aws_ssm_parameter" "dev_envname" {
  name  = "dev_envname"
  type  = "String"
  value = "DEV"
}

resource "aws_ssm_parameter" "dev_calcinstance" {
  name  = "dev_calcinstance"
  type  = "String"
  value = "i-0da38ed8aea1a1d85"
}
 
resource "aws_ssm_parameter" "dev_wmplhome" {
  name  = "dev_wmplhome"
  type  = "String"
  value = "/home/ec2-user/src/wmpldev"
}

resource "aws_ssm_parameter" "dev_rmshome" {
  name  = "dev_rmshome"
  type  = "String"
  value = "/home/ec2-user/src/RMS"
}

resource "aws_ssm_parameter" "dev_srcdir" {
  name  = "dev_srcdir"
  type  = "String"
  value = "/home/ec2-user/dev"
}

resource "aws_ssm_parameter" "dev_archdir" {
  name  = "dev_archdir"
  type  = "String"
  value = "/home/ec2-user/ukmon-shared/archive"
}

resource "aws_ssm_parameter" "dev_matchdir" {
  name  = "dev_matchdir"
  type  = "String"
  value = "/home/ec2-user/ukmon-shared/matches"
}

resource "aws_ssm_parameter" "dev_caminfo" {
  name  = "dev_caminfo"
  type  = "String"
  value = "/home/ec2-user/ukmon-shared/consolidated/camera-details.csv"
}
