resource "aws_s3_bucket" "ukmon-shared-backup" {
  bucket = "ukmon-shared-backup"
  tags = {
    "billingtag" = "ukmon"
  }
  object_lock_enabled = false
}

resource "aws_s3_bucket_lifecycle_configuration" "bkp_lifecycle_rule" {
  bucket = aws_s3_bucket.ukmon-shared-backup.id
  rule {
    id     = "MoveToArchive"
    status = "Enabled"
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }
  }
}

resource "aws_s3_bucket_logging" "ukmslogging" {
  bucket = aws_s3_bucket.ukmon-shared-backup.id

  target_bucket = "mjmmauditing"
  target_prefix = "ukmon-shared-backup/"
}

resource "aws_s3_bucket" "mjmm-ukmonarchive-co-uk" {
  bucket = "mjmm-ukmonarchive.co.uk"
  tags = {
    "billingtag" = "ukmon"
  }
}

resource "aws_s3_bucket_acl" "mjmm-ukmon_acl"{
  bucket = "mjmm-ukmonarchive.co.uk"
  acl    = "public-read"
}

resource "aws_s3_bucket_logging" "mjmm_ukmon_logging"{
  bucket = "mjmm-ukmonarchive.co.uk"
  target_bucket = "mjmmauditing"
  target_prefix = "ukmon-archive-logs/"
}

resource "aws_s3_bucket_website_configuration" "mjmm_ukmon_website" {
  bucket = "mjmm-ukmonarchive.co.uk"
  error_document { key = "error.html"}
  index_document { suffix = "index.html"}
}

resource "aws_s3_bucket_server_side_encryption_configuration" "mjmm_ukmon_encryption" {
  bucket = aws_s3_bucket.mjmm-ukmonarchive-co-uk.bucket

  rule {
    bucket_key_enabled = false
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_policy" "allow_website_access" {
  bucket = aws_s3_bucket.mjmm-ukmonarchive-co-uk.id
  policy = data.aws_iam_policy_document.websiteacesspolicy.json
}

data "aws_iam_policy_document" "websiteacesspolicy" {
  statement {
    actions = ["s3:GetObject"]
    sid     = "PublicReadGetObject"
    effect  = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
    resources = ["${aws_s3_bucket.mjmm-ukmonarchive-co-uk.arn}/*"]
  }
}
