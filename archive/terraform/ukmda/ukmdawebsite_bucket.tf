# Copyright (C) 2018-2023 Mark McIntyre
resource "aws_s3_bucket" "archsite" {
  bucket        = var.websitebucket
  force_destroy = false
  tags = {
    "billingtag" = "ukmda"
    "ukmdatype"  = "website"
  }
}

resource "aws_s3_bucket_policy" "archsite_bp" {
  bucket = var.websitebucket
  policy = jsonencode(
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "1",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity E33O69YJJ84VGS"
            },
            "Action": "s3:GetObject",
            "Resource": "${aws_s3_bucket.archsite.arn}/*"
        },
        {
            "Sid": "2",
            "Effect": "Allow",
            "Principal": {
                "AWS": [
                    "arn:aws:iam::${var.remote_account_id}:role/lambda-s3-full-access-role",
                    "arn:aws:iam::${var.remote_account_id}:role/ecsTaskExecutionRole",
                    "arn:aws:iam::${var.remote_account_id}:user/s3user",
                    "arn:aws:iam::${var.remote_account_id}:user/Mary",
                    "arn:aws:iam::${var.remote_account_id}:role/S3FullAccess",
                    "arn:aws:iam::${var.remote_account_id}:user/Mark"
                ]
            },
            "Action": [
                "s3:Put*",
                "s3:ListBucket",
                "s3:Get*",
                "s3:Delete*"
            ],
            "Resource": [
                "${aws_s3_bucket.archsite.arn}/*",
                "${aws_s3_bucket.archsite.arn}"
            ]
        },
        {
            "Sid": "4",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::${data.aws_caller_identity.current.account_id}:user/MarkMcIntyreUKM"
            },
            "Action": [
                "s3:Put*",
                "s3:ListBucket",
                "s3:Get*",
                "s3:Delete*"
            ],
            "Resource": [
                "${aws_s3_bucket.archsite.arn}/*",
                "${aws_s3_bucket.archsite.arn}"
            ]
        }
    ]
}
  )
}

resource "aws_s3_bucket_ownership_controls" "ukmdaarch_objownrule" {
  bucket = aws_s3_bucket.archsite.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_logging" "ukmdawebsitelogs" {
  bucket = aws_s3_bucket.archsite.id

  target_bucket = aws_s3_bucket.logbucket.id
  target_prefix = "website/"
}


resource "aws_s3_bucket_lifecycle_configuration" "archsitelcp" {
  bucket = aws_s3_bucket.archsite.id
  transition_default_minimum_object_size = "varies_by_storage_class"
  rule {
    status = "Enabled"
    id     = "purge old versions"
    noncurrent_version_expiration {
      noncurrent_days = 30
    }
    filter {}
  }
  rule {
    status = "Enabled"
    id     = "Transition reports to IA"
    filter {
      prefix = "reports/"
    }

    transition {
      days          = 45
      storage_class = "STANDARD_IA"
    }
  }
  rule {
    status = "Enabled"
    id     = "Transition images to IA"
    filter {
      prefix = "img/"
    }

    transition {
      days          = 45
      storage_class = "STANDARD_IA"
    }
  }
  rule {
    status = "Enabled"
    id     = "Transition CSVs to IA"
    filter {
      prefix = "browse/"
    }

    transition {
      days          = 45
      storage_class = "STANDARD_IA"
    }
  }
}

output "bucketid" { value = aws_s3_bucket.archsite.id }