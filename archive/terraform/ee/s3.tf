resource "aws_s3_bucket" "archsite" {
  bucket        = var.websitebucket
  acl           = "private"
  force_destroy = false
  tags = {
    "billingtag" = "ukmon"
  }
}
