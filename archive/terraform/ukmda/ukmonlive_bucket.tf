# Copyright (C) 2018-2023 Mark McIntyre
resource "aws_s3_bucket" "ukmdalive" {
  bucket        = var.livebucket
  force_destroy = false
  
  tags = {
    "billingtag" = "ukmda"
    "ukmdatype"  = "live"
  }
  provider = aws.eu-west-1-prov
}

resource "aws_s3_bucket_policy" "ukmdalivebp" {
  bucket   = aws_s3_bucket.ukmdalive.id
  provider = aws.eu-west-1-prov
  policy = jsonencode(
    {
      Id = "ukmda-live-bp"
      Statement = [
        {
            "Sid": "DataSyncCreateS3LocationAndTaskAccess",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::${var.eeaccountid}:role/DataSyncBetweenAccounts"
            },
            "Action": [
                "s3:GetBucketLocation",
                "s3:ListBucket",
                "s3:ListBucketMultipartUploads",
                "s3:AbortMultipartUpload",
                "s3:DeleteObject",
                "s3:GetObject",
                "s3:ListMultipartUploadParts",
                "s3:PutObject",
                "s3:GetObjectTagging",
                "s3:PutObjectTagging"
            ],
            "Resource": [
                "${aws_s3_bucket.ukmdalive.arn}",
                "${aws_s3_bucket.ukmdalive.arn}/*"
            ]
        },
        {
            "Sid": "DataSyncCreateS3Location",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::${var.eeaccountid}:role/AdministratorRole"
            },
            "Action": "s3:ListBucket",
            "Resource": "${aws_s3_bucket.ukmdalive.arn}"
        }        
      ]
      Version = "2008-10-17"
    }
  )
}
/*
resource "aws_s3_bucket_acl" "ukmdaliveacl" {
  bucket   = aws_s3_bucket.ukmdalive.id
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
*/
resource "aws_s3_bucket_lifecycle_configuration" "ukmdalivelcp" {
  bucket   = aws_s3_bucket.ukmdalive.id
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
/*
resource "aws_s3_bucket_cors_configuration" "ukmdalivecors" {
  bucket   = aws_s3_bucket.ukmdalive.id
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
*/
resource "aws_s3_bucket_logging" "ukmdalivelogs" {
  provider = aws.eu-west-1-prov
  bucket = aws_s3_bucket.ukmdalive.id
  target_bucket = aws_s3_bucket.logbucket_w1.id
  target_prefix = "ukmdalive/"
}

resource "aws_s3_bucket_public_access_block" "ukmdalive-pab" {
  provider = aws.eu-west-1-prov
  bucket = aws_s3_bucket.ukmdalive.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}


resource "aws_s3_bucket_ownership_controls" "ukmdalive_objownrule" {
  provider  = aws.eu-west-1-prov
  bucket = aws_s3_bucket.ukmdalive.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

