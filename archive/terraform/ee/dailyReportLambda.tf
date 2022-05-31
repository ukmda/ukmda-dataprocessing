#
# terraform to create the lambdas in the MJMM account
#

# the Lambda's body is being uploaded via a Zip file
# this block creates a zip file from the contents of files/src
data "archive_file" "dailyreportzip" {
  type        = "zip"
  source_dir  = "${path.root}/files/dailyreport/"
  output_path = "${path.root}/files/dailyreport.zip"
}

resource "aws_lambda_function" "dailyreportlambda" {
  provider      = aws.eu-west-1-prov
  function_name = "dailyReport"
  description   = "Daily report of matching events"
  filename      = data.archive_file.dailyreportzip.output_path
  handler       = "dailyReport.lambda_handler"
  runtime       = "python3.8"
  memory_size   = 128
  timeout       = 300
  role          = aws_iam_role.dayilreport_role.arn
  publish       = false
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
    Name        = "dailyReport"
    billingtag  = "ukmon"
    "UKMonLive" = "2"
  }
}

# ROLES
# IAM role which dictates what other AWS services the Lambda function
# may access.
resource "aws_iam_role" "dayilreport_role" {
  name               = "dailyReportRole"
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
resource "aws_iam_role_policy" "dailyreport_policy" {
  name   = "dailyReportPolicy"
  role   = aws_iam_role.dayilreport_role.id
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
		{
			"Effect": "Allow",
			"Action": "logs:CreateLogGroup",
      "Resource": "arn:aws:logs:${var.region}:${data.aws_caller_identity.current.account_id}:*"
    },
    {
			"Effect": "Allow",
      "Action": [
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:${var.region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/dailyReport:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:*",
        "s3-object-lambda:*",
        "ses:SendEmail",
        "ses:Describe*"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}

/*
*/
