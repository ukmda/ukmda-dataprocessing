data "archive_file" "copylivezip" {
  type        = "zip"
  source_dir  = "${path.root}/files/copyLive/"
  output_path = "${path.root}/files/copyLive.zip"
}

resource "aws_lambda_function" "copylivelambda" {
  provider         = aws.eu-west-1-prov
  function_name    = "CopyLiveFeed"
  description      = "Realtime replication of livestream"
  filename         = data.archive_file.copylivezip.output_path
  source_code_hash = data.archive_file.copylivezip.output_base64sha256
  handler          = "copyLive.lambda_handler"
  runtime          = "python3.8"
  memory_size      = 128
  timeout          = 300
  role             = aws_iam_role.copylive_role.arn
  publish          = false
  environment {
    variables = {
      OFFSET = "1"
      DEBUG  = "False"
    }
  }
  ephemeral_storage {
    size = 512
  }
  tags = {
    Name        = "CopyLiveFeed"
    billingtag  = "ukmda"
    "UKMonLive" = "1"
  }
}

# ROLES
# IAM role which dictates what other AWS services the Lambda function
# may access.
resource "aws_iam_role" "copylive_role" {
  name               = "copyLiveRole"
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
resource "aws_iam_role_policy" "copylive_policy" {
  name   = "copyLivePolicy"
  role   = aws_iam_role.copylive_role.id
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
      "Resource": "arn:aws:logs:${var.liveregion}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/CopyLiveFeed:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:*",
        "s3-object-lambda:*"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "copylivexacctaccess" {
  role       = aws_iam_role.copylive_role.name
  policy_arn = aws_iam_policy.crossacctpolicyecs.arn
}


resource "aws_lambda_permission" "permcopylivelambda" {
  provider         = aws.eu-west-1-prov
  statement_id   = "AllowExecutionFromS3Bucket"
  action         = "lambda:InvokeFunction"
  function_name  = aws_lambda_function.copylivelambda.arn
  principal      = "s3.amazonaws.com"
  source_account = data.aws_caller_identity.current.account_id
  source_arn     = aws_s3_bucket.ukmdalive.arn
}
