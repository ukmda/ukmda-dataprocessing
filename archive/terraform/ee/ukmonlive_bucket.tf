##############################################################################
# Copyright (c) 2018- Mark McIntyre
##############################################################################

resource "aws_s3_bucket" "ukmonlive" {
  bucket        = var.livebucket
  force_destroy = false
  tags = {
    "billingtag" = "ukmon"
    "ukmontype"  = "live"
  }
  provider = aws.eu-west-1-prov
  timeouts {}
}

resource "aws_s3_bucket_policy" "ukmonlivebp" {
  bucket   = aws_s3_bucket.ukmonlive.id
  provider = aws.eu-west-1-prov
  policy = jsonencode(
    {
      Id = "Policy1380877762691"
      Statement = [
        {
          Action = [
            "s3:GetObject",
            "s3:PutObject",
            "s3:PutObjectAcl"
          ]
          Effect    = "Allow"
          Principal = "*"
          Resource  = "arn:aws:s3:::ukmon-live/*"
          Sid       = "Stmt1380877761162"
        },
      ]
      Version = "2008-10-17"
    }
  )
}

resource "aws_s3_bucket_acl" "ukmonliveacl" {
  bucket   = aws_s3_bucket.ukmonlive.id
  provider = aws.eu-west-1-prov
  access_control_policy {
    owner {
      id = data.aws_canonical_user_id.current.id
    }

    grant {
      permission = "READ"
      grantee {
        type = "Group"
        uri  = "http://acs.amazonaws.com/groups/global/AllUsers"
      }
    }
    grant {
      permission = "READ_ACP"
      grantee {
        type = "Group"
        uri  = "http://acs.amazonaws.com/groups/s3/LogDelivery"
      }
    }
    grant {
      permission = "WRITE"
      grantee {
        type = "Group"
        uri  = "http://acs.amazonaws.com/groups/s3/LogDelivery"
      }
    }
    grant {
      permission = "FULL_CONTROL"
      grantee {
        #display_name = "ukmeteornetwork"
        id           = "c17d5e7eafb82458a2f2439be92f8dfc85cee141a142c05d1f1bb1d66dfd3f4b"
        type         = "CanonicalUser"
      }
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "ukmonlivelcp" {
  bucket   = aws_s3_bucket.ukmonlive.id
  provider = aws.eu-west-1-prov
  rule {
    status = "Enabled"
    id     = "1 months delete"
    abort_incomplete_multipart_upload {
      days_after_initiation = 30
    }
    noncurrent_version_expiration {
      noncurrent_days = 30
    }
    expiration {
      days                         = 30
      expired_object_delete_marker = false
    }
  }
}

resource "aws_s3_bucket_cors_configuration" "ukmonlivecors" {
  bucket   = aws_s3_bucket.ukmonlive.id
  provider = aws.eu-west-1-prov
  cors_rule {
    allowed_headers = [
      "*",
      "x-amz-acl",
    ]
    allowed_methods = [
      "GET",
      "HEAD",
      "POST",
      "PUT",
    ]
    allowed_origins = [
      "*",
    ]
    expose_headers  = []
    max_age_seconds = 30000
  }
}

resource "aws_s3_bucket_logging" "ukmonlivelogs" {
  bucket = aws_s3_bucket.ukmonlive.id
  provider = aws.eu-west-1-prov
  target_bucket = aws_s3_bucket.logbucket_w1.id
  target_prefix = "ukmonlive/"
}


/*
resource "aws_s3_bucket_ownership_controls" "ukmonlive_objownrule" {
  provider  = aws.eu-west-1-prov
  bucket = aws_s3_bucket.ukmonlive.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

*/
