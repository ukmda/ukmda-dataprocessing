# Copyright (C) 2018-2023 Mark McIntyre

resource "aws_s3_bucket" "logbucket" {
  bucket        = "ukmda-s3-access-logs"
  force_destroy = false
  tags = {
    "billingtag" = "ukmda"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "ukmdalogslcp" {
  bucket = aws_s3_bucket.logbucket.id
  rule {
    status = "Enabled"
    id     = "purge old versions"
    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
  rule {
    id     = "purge old ukmda-shared logs"
    status = "Enabled"

    expiration {
      days                         = 10
      expired_object_delete_marker = false
    }

    filter {
      prefix = "ukmdashared/"
    }

    noncurrent_version_expiration {
      noncurrent_days = 5
    }
  }
  rule {
    id     = "purge old website logs"
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
    id     = "purge old cloudfront logs"
    status = "Enabled"

    expiration {
      days                         = 10
      expired_object_delete_marker = false
    }

    filter {
      prefix = "cdn/"
    }

    noncurrent_version_expiration {
      noncurrent_days = 5
    }
  }

}

resource "aws_s3_bucket_public_access_block" "logging-w2-pab" {
  bucket = aws_s3_bucket.logbucket.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "logging_objownrule" {
  bucket = aws_s3_bucket.logbucket.id

  rule {
    object_ownership = "BucketOwnerPreferred" # "BucketOwnerEnforced"
  }
}


##################################
## region 1 logging bucket
##################################


resource "aws_s3_bucket" "logbucket_w1" {
  bucket        = "ukmda-s3-access-logs-w1"
  force_destroy = false
  tags = {
    "billingtag" = "ukmda"
  }
  provider = aws.eu-west-1-prov
}

resource "aws_s3_bucket_lifecycle_configuration" "ukmdalogslcp_w1" {
  bucket = aws_s3_bucket.logbucket_w1.id
  provider = aws.eu-west-1-prov
  rule {
    status = "Enabled"
    id     = "purge old versions"
    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
  rule {
    id     = "purge old ukmda-live logs"
    status = "Enabled"

    expiration {
      days                         = 10
      expired_object_delete_marker = false
    }

    filter {
      prefix = "ukmdalive/"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "logging-w1-pab" {
  bucket = aws_s3_bucket.logbucket_w1.id
  provider = aws.eu-west-1-prov

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "logging_w1_bjownrule" {
  bucket = aws_s3_bucket.logbucket_w1.id
  provider = aws.eu-west-1-prov

  rule {
    object_ownership = "BucketOwnerPreferred" # "BucketOwnerEnforced"
  }
}
