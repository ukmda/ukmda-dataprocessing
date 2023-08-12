# Copyright (C) 2018-2023 Mark McIntyre

# encryption/decryption key in the AWS KMS keystore
resource "aws_kms_key" "container_key" {
  description = "My KMS Key"
  tags = {
    "billingtag" = "ukmon"
  }
}

# ssh keys
resource "aws_key_pair" "marks_key2" {
  key_name = "marks_key2"
  public_key = file("./ssh-keys/markskey.pub")
  tags = {
    "billingtag" = "Management"
  }
}

# ssh keys
resource "aws_key_pair" "marks_key" {
  key_name = "markskey"
  public_key = file("./ssh-keys/markskey.pub")
  tags = {
    "billingtag" = "Management"
  }
}