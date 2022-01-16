resource "aws_s3_bucket" "ukmon-shared-backup" {
  bucket = "ukmon-shared-backup"
  tags = {
    "billingtag" = "ukmon"
  }
  lifecycle_rule {
    abort_incomplete_multipart_upload_days = 0
    enabled                                = true
    id                                     = "MoveToArchive"
    tags                                   = {}

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }
  }
}

resource "aws_s3_bucket" "mjmm-ukmonarchive-co-uk" {
  bucket = "mjmm-ukmonarchive.co.uk"
  acl    = "public-read"
  tags = {
    "billingtag" = "ukmon"
  }
  logging {
    target_bucket = "mjmmauditing"
    target_prefix = "ukmon-archive-logs/"
  }
  server_side_encryption_configuration {
    rule {
      bucket_key_enabled = false

      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
  website {
    error_document = "error.html"
    index_document = "index.html"
  }
}

resource "aws_s3_bucket_policy" "allow_website_access" {
  bucket = aws_s3_bucket.mjmm-ukmonarchive-co-uk.id
  policy = data.aws_iam_policy_document.websiteacesspolicy.json
}

data "aws_iam_policy_document" "websiteacesspolicy" {
      statement        {
          actions = ["s3:GetObject"]
          sid = "PublicReadGetObject"
          effect = "Allow"
          principals { 
              type="AWS"
              identifiers= ["*"] 
              }
          resources = ["${aws_s3_bucket.mjmm-ukmonarchive-co-uk.arn}/*"]
        }
}