# Copyright (C) 2018-2023 Mark McIntyre
#
# bucket notifications that trigger lambdas
# 

# Lambdas created by SAM functions
data "aws_lambda_function" "monitorlive" {
  function_name = "monitorLive"
  provider         = aws.eu-west-1-prov
}



resource "aws_s3_bucket_notification" "ukmda_live_notification" {
  bucket = aws_s3_bucket.ukmdalive.id
  provider         = aws.eu-west-1-prov
  lambda_function {
    lambda_function_arn = data.aws_lambda_function.monitorlive.arn
    id                  = "allfiles"
    events = [
      "s3:ObjectCreated:*"
    ]
    filter_suffix       = ".jpg"
  }
}

# allow the function to be invoked from an S3 bucket. 
resource "aws_lambda_permission" "permmonitorlive" {
  provider         = aws.eu-west-1-prov
  statement_id   = "AllowExecutionFromS3Bucket"
  action         = "lambda:InvokeFunction"
  function_name  = data.aws_lambda_function.monitorlive.arn
  principal      = "s3.amazonaws.com"
  source_account = data.aws_caller_identity.current.account_id
  source_arn     = aws_s3_bucket.ukmdalive.arn
}

