resource "aws_s3_bucket" "logbucket" {
  bucket        = "ukmon-s3-access-logs"
  force_destroy = false
  tags = {
    "billingtag" = "ukmon"
    "ukmontype"  = "logs"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "ukmonlogslcp" {
  bucket = aws_s3_bucket.logbucket.id
  rule {
    status = "Enabled"
    id     = "purge old versions"
    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
  rule {
    id     = "purge old ukmon-shared logs"
    status = "Enabled"

    expiration {
      days                         = 10
      expired_object_delete_marker = false
    }

    filter {
      prefix = "ukmonshared/"
    }

    noncurrent_version_expiration {
      noncurrent_days = 5
    }
  }
  rule {
    id     = "purge old ukmeteornetworkarchive logs"
    status = "Enabled"

    expiration {
      days                         = 10
      expired_object_delete_marker = false
    }

    filter {
      prefix = "archsite/"
    }

    noncurrent_version_expiration {
      noncurrent_days = 5
    }
  }
  rule {
    id     = "purge old ukmon-live logs"
    status = "Enabled"

    expiration {
      days                         = 5
      expired_object_delete_marker = false
    }

    filter {
      prefix = "ukmonlive/"
    }

    noncurrent_version_expiration {
      noncurrent_days = 5
    }
  }
}