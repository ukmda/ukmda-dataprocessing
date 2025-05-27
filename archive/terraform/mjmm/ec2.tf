# Copyright (C) 2018-2023 Mark McIntyre

# built in aws_infra project as shared resources
data "aws_security_group" "ec2publicsg" {
    name        = "ec2PublicSG"
}
data "aws_key_pair" "marks_key" {
  key_name           = "markskey"
}


resource "aws_instance" "ukmonhelper_g" {
  ami                  = "ami-0c127ddea5a07804b"
  instance_type        = "t4g.micro"
  iam_instance_profile = aws_iam_instance_profile.S3FullAccess.name
  key_name             = data.aws_key_pair.marks_key.key_name
  security_groups      = [data.aws_security_group.ec2publicsg.name]

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
  tags = {
    billingtag = "ukmon"
    Name       = "ukmonhelper_eip"
  }
}
