resource "aws_s3_bucket" "b" {
  bucket        = var.bucket_name
  acl           = "private"
  force_destroy = false
  tags = {
    "billingtag" = "ukmon"
  }
}
