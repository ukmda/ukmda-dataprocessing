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
    object_ownership = "BucketOwnerPreferred"
  }
}
