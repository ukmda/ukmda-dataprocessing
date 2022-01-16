resource "aws_instance" "ukmonhelper" {
  ami                  = "ami-0a669382ea0feb73a"
  instance_type        = "t2.micro"
  iam_instance_profile = "S3FullAccess"
  tags = {
    "Name"       = "UKMonHelper"
    "billingtag" = "ukmon"
    "project"    = "UKMonHelper"
  }
}

resource "aws_instance" "CalcEngine3ARM" {
  ami                  = "ami-05c6a3a1350a69209"
  instance_type        = "c6g.4xlarge"
  iam_instance_profile = "S3FullAccess"
  tags = {
    "Name"       = "Calcengine3Arm"
    "name"       = "Calcengine3"
    "billingtag" = "ukmon"
    "project"    = "UkmonHelperBigx2"
  }
}

resource "aws_instance" "x16coreAWS" {
  ami                  = "ami-03ac5a9b225e99b02"
  instance_type        = "c5.4xlarge"
  iam_instance_profile = "S3FullAccess"
  tags = {
    "Name"       = "16coreAWS"
    "billingtag" = "ukmon"
    "project"    = "UKMonHelperBig"
  }
}
