# Copyright (C) 2018-2023 Mark McIntyre
resource "aws_s3_bucket" "archsite" {
  bucket        = var.websitebucket
  force_destroy = false
  tags = {
    "billingtag" = "ukmda"
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
    resources = ["${aws_s3_bucket.archsite.arn}/*"]
    actions   = ["s3:GetObject"]

    principals {
      type        = "AWS"
      identifiers = [aws_cloudfront_origin_access_identity.archsite_oaid.iam_arn]
    }
  }

  statement {
    sid    = "2"
    effect = "Allow"
    resources = [
      "${aws_s3_bucket.archsite.arn}/*",
      "${aws_s3_bucket.archsite.arn}"
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
        "arn:aws:iam::${var.remote_account_id}:role/S3FullAccess",
        "arn:aws:iam::${var.remote_account_id}:role/lambda-s3-full-access-role",
        "arn:aws:iam::${var.remote_account_id}:role/ecsTaskExecutionRole",
        "arn:aws:iam::${var.remote_account_id}:user/Mary",
        "arn:aws:iam::${var.remote_account_id}:user/Mark",
        "arn:aws:iam::${var.remote_account_id}:user/s3user",
      ]
    }
  }

  statement {
    sid    = "4"
    effect = "Allow"
    resources = [
      "${aws_s3_bucket.archsite.arn}/*",
      "${aws_s3_bucket.archsite.arn}"
    ]

    actions = [
      "s3:Put*",
      "s3:Get*",
      "s3:Delete*",
      "s3:ListBucket"
    ]

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:user/MarkMcIntyreUKM"]
    }
  }
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