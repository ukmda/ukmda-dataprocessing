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

resource "aws_s3_bucket_notification" "ukmonlive_trigger" {
  bucket = aws_s3_bucket.ukmonlive.id
  provider         = aws.eu-west-1-prov
  lambda_function {
    lambda_function_arn = aws_lambda_function.replicatelive.arn
    id                  = "liveimages"
    events = [  "s3:ObjectCreated:*"  ]
    filter_suffix = ".xml"
  }
}

data "archive_file" "replicatelive" {
  type        = "zip"
  source_dir  = "${path.root}/files/replicatelive/"
  output_path = "${path.root}/files/replicatelive.zip"
}

resource "aws_lambda_function" "replicatelive" {
  provider         = aws.eu-west-1-prov
  function_name    = "replicatelive"
  description      = "Create backup of livestream"
  filename         = data.archive_file.replicatelive.output_path
  source_code_hash = data.archive_file.replicatelive.output_base64sha256
  handler          = "replicatelive.lambda_handler"
  runtime          = "python3.8"
  memory_size      = 128
  timeout          = 300
  role             = aws_iam_role.replicatelive_role.arn
  publish          = false
  tags = {
    Name        = "replicatelive"
    billingtag  = "ukmon"
    "UKMonLive" = "2"
  }
}

# ROLES
# IAM role which dictates what other AWS services the Lambda function
# may access.
resource "aws_iam_role" "replicatelive_role" {
  name               = "replicatelive"
  path               = "/service-role/"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

# POLICIES granted to the IAM role used by the Lambda function
resource "aws_iam_role_policy" "replicatelive_policy" {
  name   = "replicatelivePolicy"
  role   = aws_iam_role.replicatelive_role.id
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
		{
			"Effect": "Allow",
			"Action": "logs:CreateLogGroup",
      "Resource": "arn:aws:logs:${var.liveregion}:${data.aws_caller_identity.current.account_id}:*"
    },
    {
			"Effect": "Allow",
      "Action": [
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:${var.liveregion}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/replicatelive:*"
    },
    {
      "Effect": "Allow",
      "Action": [ "s3:*" ],
      "Resource": [
        "arn:aws:s3:::ukmon-live",
        "arn:aws:s3:::ukmon-live/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [ "s3:Put*" ],
      "Resource": 
        [
          "arn:aws:s3:::ukmda-live",
          "arn:aws:s3:::ukmda-live/*"
        ]
    }
  ]
}
EOF
}

resource "aws_lambda_permission" "replicatelive" {
  provider         = aws.eu-west-1-prov
  statement_id   = "AllowExecutionFromS3Bucket"
  action         = "lambda:InvokeFunction"
  function_name  = aws_lambda_function.replicatelive.arn
  principal      = "s3.amazonaws.com"
  source_account = data.aws_caller_identity.current.account_id
  source_arn     = aws_s3_bucket.ukmonlive.arn
}
