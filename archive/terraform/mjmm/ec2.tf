resource "aws_instance" "ukmonhelper" {
  ami                  = "ami-0a669382ea0feb73a"
  instance_type        = "t3a.micro"
  iam_instance_profile = "S3FullAccess"
  key_name             = "markskey"
  #security_groups = [aws_security_group.launch-wizard-4.id]
  tags = {
    "Name"       = "UKMonHelper"
    "billingtag" = "ukmon"
    "project"    = "UKMonHelper"
  }
}

resource "aws_instance" "CalcEngine4ARM" {
  #ami                  = "ami-05c6a3a1350a69209"
  ami                  = "ami-0e15ed7362de6ef5b" # this is my AMI
  instance_type        = "c6g.4xlarge"
  iam_instance_profile = "S3FullAccess"
  #key_name = aws_key_pair.marks_keys.key_name
  #security_groups = [aws_security_group.launch-wizard-4.id]
  tags = {
    "Name"       = "Calcengine4Arm"
    "name"       = "Calcengine4"
    "billingtag" = "ukmon"
    "project"    = "UkmonHelperBigx2"
  }
  root_block_device {
    tags = {
      "Name" = "calcengine4arm"
      "billingtag" = "ukmon"
      "project"    = "UkmonHelperBigx2"
    }
    volume_size = 40
  }
}

resource "aws_instance" "x16coreAWS" {
  ami                  = "ami-03ac5a9b225e99b02"
  instance_type        = "c5.4xlarge"
  iam_instance_profile = "S3FullAccess"
  #key_name = aws_key_pair.marks_keys.key_name
  #security_groups = [aws_security_group.launch-wizard-4.id]
  tags = {
    "Name"       = "16coreAWS"
    "billingtag" = "ukmon"
    "project"    = "UKMonHelperBig"
  }
}
