data "archive_file" "monitorlivezip" {
  type        = "zip"
  source_dir  = "${path.root}/files/monitorLiveFeed/"
  output_path = "${path.root}/files/monitorLiveFeed.zip"
}

resource "aws_lambda_function" "monitorlivelambda" {
  provider         = aws.eu-west-1-prov
  function_name    = "MonitorLiveFeed"
  description      = "Realtime tracking of brightness data"
  filename         = data.archive_file.monitorlivezip.output_path
  source_code_hash = data.archive_file.monitorlivezip.output_base64sha256
  handler          = "monitorLiveFeed.lambda_handler"
  runtime          = "python3.11"
  memory_size      = 128
  timeout          = 300
  role             = aws_iam_role.monitorlive_role.arn
  publish          = false
  architectures    = ["arm64"]
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
data "template_file" "livemonitorlambdatempl" {
  template = file("files/policies/monitorlive-lambda.json")
  vars = {
    liveregion = var.liveregion
    accountid = data.aws_caller_identity.current.account_id
  }

}

resource "aws_iam_role_policy" "monitorlive_policy" {
  name   = "monitorLivePolicy"
  role   = aws_iam_role.monitorlive_role.id
  policy = data.template_file.livemonitorlambdatempl.rendered
}  

resource "aws_lambda_permission" "permmonitorlivelambda" {
  provider         = aws.eu-west-1-prov
  statement_id   = "AllowExecutionFromS3Bucket"
  action         = "lambda:InvokeFunction"
  function_name  = aws_lambda_function.monitorlivelambda.arn
  principal      = "s3.amazonaws.com"
  source_account = data.aws_caller_identity.current.account_id
  source_arn     = aws_s3_bucket.ukmdalive.arn
}
