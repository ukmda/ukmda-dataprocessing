resource "aws_s3_bucket" "archsite" {
  bucket        = var.websitebucket
  force_destroy = false
  tags = {
    "billingtag" = "ukmon"
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
    sid       = "2"
    effect    = "Allow"
    resources = ["arn:aws:s3:::ukmeteornetworkarchive/*"]

    actions = [
      "s3:PutObjectACL",
      "s3:PutObject",
      "s3:GetObject",
      "s3:DeleteObject",
    ]

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::317976261112:user/Mark"]
    }
  }

  statement {
    sid       = "3"
    effect    = "Allow"
    resources = ["arn:aws:s3:::ukmeteornetworkarchive"]
    actions   = ["s3:ListBucket"]

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::317976261112:user/Mark"]
    }
  }

  statement {
    sid       = "4"
    effect    = "Allow"
    resources = ["arn:aws:s3:::ukmeteornetworkarchive/*"]

    actions = [
      "s3:PutObjectACL",
      "s3:PutObject",
      "s3:GetObjectACL",
      "s3:GetObject",
      "s3:DeleteObject",
    ]

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:user/MarkMcIntyre"]
    }
  }

  statement {
    sid       = "5"
    effect    = "Allow"
    resources = ["arn:aws:s3:::ukmeteornetworkarchive"]
    actions   = ["s3:ListBucket"]

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:user/MarkMcIntyre"]
    }
  }
}