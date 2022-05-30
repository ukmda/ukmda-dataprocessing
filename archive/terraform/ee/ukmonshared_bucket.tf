resource "aws_s3_bucket" "ukmonshared" {
  bucket        = var.sharedbucket
  force_destroy = false
  tags = {
    "billingtag" = "ukmon"
  }
}

resource "aws_s3_bucket_policy" "ukmonsharedbp" {
  bucket = aws_s3_bucket.ukmonshared.id
  policy = jsonencode(
    {
      Statement = [
        {
          Action = [
            "s3:ListBucket",
            "s3:GetObject",
          ]
          Effect = "Allow"
          Principal = {
            AWS = "arn:aws:iam::317976261112:root"
          }
          Resource = [
            "arn:aws:s3:::ukmon-shared/*",
            "arn:aws:s3:::ukmon-shared",
          ]
          Sid = "DelegateS3Access"
        },
      ]
      Version = "2012-10-17"
    }
  )
}

resource "aws_s3_bucket_acl" "ukmonsharedacl" {
  bucket = aws_s3_bucket.ukmonshared.id
  access_control_policy {
    owner {
      id = data.aws_canonical_user_id.current.id
    }
    grant {
      grantee {
        id   = data.aws_canonical_user_id.current.id
        type = "CanonicalUser"
      }
      permission = "FULL_CONTROL"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "ukmonsharedlcp" {
  bucket = aws_s3_bucket.ukmonshared.id
  rule {
    status = "Enabled"
    id     = "purge old versions"
    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
  rule {
    status = "Enabled"
    id     = "Transition to IA"
    filter {
      prefix = "archive/"
    }

    transition {
      days          = 60
      storage_class = "STANDARD_IA"
    }
  }
}

resource "aws_s3_bucket_cors_configuration" "ukmonsharedcors" {
  bucket = aws_s3_bucket.ukmonshared.id
  cors_rule {
    allowed_headers = [
      "*",
    ]
    allowed_methods = [
      "HEAD",
      "GET",
      "PUT",
      "POST",
      "DELETE",
    ]
    allowed_origins = [
      "https://markmcintyreastro.co.uk",
    ]
    expose_headers = [
      "ETag",
      "x-amz-meta-custom-header",
    ]
    max_age_seconds = 0
  }
}