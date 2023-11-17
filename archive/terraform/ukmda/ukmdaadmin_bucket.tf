resource "aws_s3_bucket" "adminbucket" {
  bucket        = var.adminbucket
  force_destroy = false
  tags = {
    "billingtag" = "ukmda"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "adminbucketlcp" {
  bucket = aws_s3_bucket.adminbucket.id
  rule {
    id     = "purge old emails"
    status = "Enabled"
    expiration {
      days                         = 30
      expired_object_delete_marker = false
    }
    filter {
      prefix = "email/"
    }
    noncurrent_version_expiration {
      noncurrent_days = 5
    }
  }
}

resource "aws_s3_bucket_public_access_block" "adminbucketpab" {
  bucket = aws_s3_bucket.adminbucket.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "adminbucket_objownrule" {
  bucket = aws_s3_bucket.adminbucket.id
  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_policy" "adminbucket_bp" {
  bucket = aws_s3_bucket.adminbucket.id
  policy = jsonencode(
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowSESPuts",
            "Effect": "Allow",
            "Principal": {
                "Service": "ses.amazonaws.com"
            },
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::${aws_s3_bucket.adminbucket.id}/*",
            "Condition": {
                "StringEquals": {
                    "aws:Referer": "${data.aws_caller_identity.current.account_id}"
                }
            }
        }
    ]
})
}
