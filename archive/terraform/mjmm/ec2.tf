# Copyright (C) 2018-2023 Mark McIntyre

resource "aws_instance" "ukmonhelper" {
  ami                  = "ami-0a669382ea0feb73a"
  instance_type        = "t3a.micro"
  iam_instance_profile = aws_iam_instance_profile.S3FullAccess.name
  key_name             = aws_key_pair.marks_key.key_name
  security_groups      = [aws_security_group.launch-wizard-4.name]

  root_block_device {
    tags = {
      "Name"       = "UKMonHelperVol"
      "billingtag" = "ukmon"
      "project"    = "UKMonHelper"
    }
    volume_size = 50
    volume_type = "gp3"
    throughput = 125
    iops = 3000
  }

  tags = {
    "Name"       = "UKMonHelper"
    "billingtag" = "ukmon"
    "project"    = "UKMonHelper"
  }
}

resource "aws_instance" "ukmonhelper_g" {
  ami                  = "ami-0bba6371ce54738a5"
  instance_type        = "t4g.micro"
  iam_instance_profile = aws_iam_instance_profile.S3FullAccess.name
  key_name             = aws_key_pair.marks_key.key_name
  security_groups      = [aws_security_group.ec2publicsg.name]

  root_block_device {
    tags = {
      "Name"       = "UKMonHelperVol2"
      "billingtag" = "ukmon"
      "project"    = "UKMonHelper2"
    }
    volume_size = 50
    volume_type = "gp3"
    throughput = 125
    iops = 3000
    encrypted = true
    kms_key_id = aws_kms_key.container_key.id
  }

  tags = {
    "Name"       = "UKMonHelper2"
    "billingtag" = "ukmon"
    "project"    = "UKMonHelper2"
  }
}

resource "aws_instance" "backuprunner" {
  ami                  = "ami-0d729d2846a86a9e7"
  instance_type        = "t3a.medium"
  iam_instance_profile = aws_iam_instance_profile.S3FullAccess.name
  key_name             = aws_key_pair.marks_key.key_name
  security_groups      = [aws_security_group.ec2publicsg.name]
  tags = {
    "Name"       = "BackupRunner"
    "billingtag" = "ukmon"
  }
  user_data                   = file("files/backuprunner/userdata.sh")
  user_data_replace_on_change = false
}
