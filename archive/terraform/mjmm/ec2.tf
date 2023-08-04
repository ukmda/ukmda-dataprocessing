# Copyright (C) 2018-2023 Mark McIntyre

/*
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
# elastic IP attached to the ukmonhelper server
resource "aws_eip" "ukmonhelper" {
  instance = aws_instance.ukmonhelper.id
  vpc      = true
  tags = {
    billingtag = "ukmon"
  }
}
# elastic network interface attached to the ukmonhelper server
resource "aws_network_interface" "ukmon_if" {
  subnet_id                 = aws_subnet.ec2Subnet.id
  private_ips               = ["172.31.12.116"]
  security_groups           = [aws_security_group.launch-wizard-4.id]
  ipv6_address_list_enabled = false
  tags = {
    "Name"       = "ukmonhelper_if"
    "billingtag" = "ukmon"
  }
  attachment {
    instance     = aws_instance.ukmonhelper.id
    device_index = 0
  }
}
*/


resource "aws_instance" "ukmonhelper_g" {
  ami                  = "ami-0c127ddea5a07804b"
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
    kms_key_id = aws_kms_key.container_key.arn
  }

  tags = {
    "Name"       = "UKMonHelper2"
    "billingtag" = "ukmon"
    "project"    = "UKMonHelper2"
  }
}

resource "aws_eip" "ukmonhelper2" {
  instance = aws_instance.ukmonhelper_g.id
  vpc      = true
  tags = {
    billingtag = "ukmon"
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
