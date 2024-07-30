# Copyright (C) 2018-2023 Mark McIntyre

# encryption/decryption key in the AWS KMS keystore
resource "aws_kms_key" "container_key" {
  description = "My KMS Key"
  tags = {
    "billingtag" = "ukmon"
  }
}
