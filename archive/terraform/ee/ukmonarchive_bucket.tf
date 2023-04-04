# Copyright (C) 2018-2023 Mark McIntyre
resource "aws_s3_bucket" "archsite" {
  bucket        = var.websitebucket
  force_destroy = false
  tags = {
    "billingtag" = "ukmon"
    "ukmontype"  = "archive"
  }
}

resource "aws_s3_bucket_policy" "archsite_bp" {
  bucket = var.websitebucket
  policy = data.aws_iam_policy_document.archsite_bp_data.json
}

data "aws_iam_policy_document" "archsite_bp_data" {
  statement {
    sid       = "1"
    effect    = "Allow"
    resources = ["arn:aws:s3:::ukmeteornetworkarchive/*"]
    actions   = ["s3:GetObject"]

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity E18JX1UO8FC7NT"]
    }
  }

  statement {
    sid    = "2"
    effect = "Allow"
    resources = [
      "arn:aws:s3:::ukmeteornetworkarchive/*",
      "arn:aws:s3:::ukmeteornetworkarchive"
    ]

    actions = [
      "s3:Put*",
      "s3:ListBucket",
      "s3:Get*",
      "s3:Delete*",
    ]

    principals {
      type = "AWS"
      identifiers = [
        "arn:aws:iam::317976261112:role/S3FullAccess",
        "arn:aws:iam::317976261112:role/lambda-s3-full-access-role",
        "arn:aws:iam::317976261112:role/ecsTaskExecutionRole",
        "arn:aws:iam::317976261112:user/Mary",
        "arn:aws:iam::317976261112:user/Mark",
        "arn:aws:iam::317976261112:user/s3user",
      ]
    }
  }

  statement {
    sid    = "4"
    effect = "Allow"
    resources = [
      "arn:aws:s3:::ukmeteornetworkarchive/*",
      "arn:aws:s3:::ukmeteornetworkarchive"
    ]

    actions = [
      "s3:Put*",
      "s3:Get*",
      "s3:Delete*",
      "s3:ListBucket"
    ]

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:user/MarkMcIntyre"]
    }
  }
}

resource "aws_s3_bucket_ownership_controls" "ukmonarch_objownrule" {
  bucket = aws_s3_bucket.archsite.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_logging" "ukmonwebsitelogs" {
  bucket = aws_s3_bucket.archsite.id

  target_bucket = aws_s3_bucket.logbucket.id
  target_prefix = "archsite/"
}


resource "aws_s3_bucket_lifecycle_configuration" "archsitelcp" {
  bucket = aws_s3_bucket.archsite.id
  rule {
    status = "Enabled"
    id     = "purge old versions"
    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
  rule {
    status = "Enabled"
    id     = "Transition reports to IA"
    filter {
      prefix = "/reports"
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
      prefix = "/img"
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
      prefix = "/browse"
    }

    transition {
      days          = 45
      storage_class = "STANDARD_IA"
    }
  }
}
