data "archive_file" "monitorlivezip" {
  type        = "zip"
  source_dir  = "${path.root}/files/curateLive/"
  output_path = "${path.root}/files/curateLive.zip"
}

resource "aws_lambda_function" "monitorlivelambda" {
  provider         = aws.eu-west-1-prov
  function_name    = "MonitorLiveFeed"
  description      = "Realtime tracking of brightness data"
  filename         = data.archive_file.monitorlivezip.output_path
  source_code_hash = data.archive_file.monitorlivezip.output_base64sha256
  handler          = "curateLive.lambda_handler"
  runtime          = "python3.8"
  memory_size      = 128
  timeout          = 300
  role             = aws_iam_role.monitorlive_role.arn
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
    Name        = "MonitorLiveFeed"
    billingtag  = "ukmda"
    "UKMonLive" = "1"
  }
}

# ROLES
# IAM role which dictates what other AWS services the Lambda function
# may access.
resource "aws_iam_role" "monitorlive_role" {
  name               = "monitorLiveRole"
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
resource "aws_iam_role_policy" "monitorlive_policy" {
  name   = "monitorLivePolicy"
  role   = aws_iam_role.monitorlive_role.id
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
      "Resource": "arn:aws:logs:${var.liveregion}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/MonitorLiveFeed:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:*",
        "s3-object-lambda:*",
        "ses:SendEmail",
        "ses:Describe*",
        "dynamodb:*"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_lambda_permission" "permmonitorlivelambda" {
  provider         = aws.eu-west-1-prov
  statement_id   = "AllowExecutionFromS3Bucket"
  action         = "lambda:InvokeFunction"
  function_name  = aws_lambda_function.monitorlivelambda.arn
  principal      = "s3.amazonaws.com"
  source_account = "822069317839"
  source_arn     = aws_s3_bucket.ukmdalive.arn
}
