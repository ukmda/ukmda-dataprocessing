# Copyright (C) 2018-2023 Mark McIntyre
resource "aws_s3_bucket" "ukmdashared" {
  bucket        = var.sharedbucket
  force_destroy = false
  tags = {
    "billingtag" = "ukmda"
    "ukmdatype"  = "datastore"
  }
}

resource "aws_s3_bucket_policy" "ukmdasharedbp" {
  bucket = aws_s3_bucket.ukmdashared.id
  policy = jsonencode(
    {
      Statement = [
        {
          Action = [
            "s3:ListBucket",
            "s3:Get*",
            "s3:Put*",
            "s3:Delete*"
          ]
          Effect = "Allow"
          Principal = {
            AWS = [
              "arn:aws:iam::${var.remote_account_id}:role/S3FullAccess", # role used by lambdas
              "arn:aws:iam::${var.remote_account_id}:role/lambda-s3-full-access-role", # role used by SAM functions
              "arn:aws:iam::${var.remote_account_id}:role/ecsTaskExecutionRole", # role used by ECS tasks
              "arn:aws:iam::${var.remote_account_id}:user/Mary",
              "arn:aws:iam::${var.remote_account_id}:user/Mark",
              "arn:aws:iam::${var.remote_account_id}:user/s3user", # not sure this is needed
            ]
          }
          Resource = [
            "${aws_s3_bucket.ukmdashared.arn}/*",
            "${aws_s3_bucket.ukmdashared.arn}",
          ]
          Sid = "DelegateS3Access"
        },
        {
            "Sid": "BlockAccessToAdmin",
            "Effect": "Deny",
            "Principal": "*",
            "Action": "s3:*",
            "Resource": "arn:aws:s3:::ukmda-shared/admin/*",
            "Condition": {
                "StringNotLike": {
                    "aws:userId": [ # update with new relevant IDs
                        "AIDASVSZXPTTB3UZT4E2B",  # MarkMcIntyreUKM
                        #"AIDA36ZZGKDHXYCBTWWC2",  # eastbourne
                        #"AIDA36ZZGKDHZAWQZON7B",  # loscoe
                        #"AIDA36ZZGKDH4LW3WF2GJ",  # Church_Cro
                        #"AIDA36ZZGKDHWBV7ZQISQ",  # chard
                        "AROAUUCG4WH4GFCTQIKH3:*", # S3FullAccess in MJMM account
                        #"AROA36ZZGKDHWAMYFNTWV:*", # DailyReportRole in ee account
                        "AROASVSZXPTTHKOAARJ2T:*", # dailyReportRole in mda account
                        "${data.aws_caller_identity.current.account_id}"            # root account
                      ]
                }
            }
        },
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
                "${aws_s3_bucket.ukmdashared.arn}",
                "${aws_s3_bucket.ukmdashared.arn}/*"
            ]
        },
        {
            "Sid": "DataSyncCreateS3Location",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::${var.eeaccountid}:role/AdministratorRole"
            },
            "Action": "s3:ListBucket",
            "Resource": "${aws_s3_bucket.ukmdashared.arn}"
        }
      ]
      Version = "2012-10-17"
    }
  )
}

resource "aws_s3_bucket_acl" "ukmdasharedacl" {
  bucket = aws_s3_bucket.ukmdashared.id
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

resource "aws_s3_bucket_lifecycle_configuration" "ukmdasharedlcp" {
  bucket = aws_s3_bucket.ukmdashared.id
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
      days          = 45
      storage_class = "STANDARD_IA"
    }
  }
  rule {
    id     = "purge athena queries"
    status = "Enabled"

    expiration {
      days                         = 2
      expired_object_delete_marker = false
    }

    filter {
      prefix = "tmp/fromglue/"
    }

    noncurrent_version_expiration {
      noncurrent_days = 2
    }
  }
  rule {
    id     = "purge distrib logs"
    status = "Enabled"

    expiration {
      days                         = 30
      expired_object_delete_marker = false
    }

    filter {
      prefix = "matches/distrib/logs/"
    }

    noncurrent_version_expiration {
      noncurrent_days = 5
    }
  }
  rule {
    id     = "purge distrib backups"
    status = "Enabled"

    expiration {
      days                         = 60
      expired_object_delete_marker = false
    }

    filter {
      prefix = "matches/distrib/done/"
    }

    noncurrent_version_expiration {
      noncurrent_days = 10
    }
  }
}

resource "aws_s3_bucket_cors_configuration" "ukmdasharedcors" {
  bucket = aws_s3_bucket.ukmdashared.id
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

resource "aws_s3_bucket_ownership_controls" "ukmdashare_objownrule" {
  bucket = aws_s3_bucket.ukmdashared.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_logging" "ukmdasharedlogs" {
  bucket = aws_s3_bucket.ukmdashared.id

  target_bucket = aws_s3_bucket.logbucket.id
  target_prefix = "ukmdashared/"
}

resource "aws_s3_bucket_public_access_block" "ukmdashared-pab" {
  bucket = aws_s3_bucket.ukmdashared.id

  block_public_acls       = false
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
