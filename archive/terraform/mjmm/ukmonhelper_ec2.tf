# Copyright (C) 2018- Mark McIntyre

data "aws_security_group" "ec2publicsg" {
  name = "ec2PublicSG"
}

data "aws_key_pair" "marks_key" {
  key_name = "markskey"
}

data "aws_kms_key" "container_key" {
  key_id = "e9b72945-eaac-4452-9708-93963b09976d"
}

data "aws_iam_instance_profile" "S3FullAccess" {
  name = "S3FullAccess"
}

resource "aws_instance" "ukmonhelper_g" {
  ami                  = "ami-0c127ddea5a07804b"
  instance_type        = "t4g.micro"
  iam_instance_profile = data.aws_iam_instance_profile.S3FullAccess.name
  key_name             = data.aws_key_pair.marks_key.key_name
  security_groups      = [data.aws_security_group.ec2publicsg.name]
  force_destroy        = false

  root_block_device {
    tags = {
      "Name"       = "UKMonHelperVol2"
      "billingtag" = "ukmon"
      "project"    = "UKMonHelper2"
    }
    volume_size = 50
    volume_type = "gp3"
    throughput  = 125
    iops        = 3000
    encrypted   = true
    kms_key_id  = data.aws_kms_key.container_key.arn
  }

  tags = {
    "Name"          = "UKMonHelper2"
    "billingtag"    = "ukmon"
    "project"       = "UKMonHelper2"
    "Route53FQDN"   = "ukmonhelper.markmcintyreastro.co.uk"
    "DNSRecordType" = "A"
  }
}

resource "aws_eip" "ukmonhelper2" {
  instance = aws_instance.ukmonhelper_g.id
  tags = {
    billingtag = "ukmon"
    Name       = "ukmonhelper_eip"
  }
}
