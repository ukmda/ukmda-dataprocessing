# Copyright (C) 2018-2023 Mark McIntyre
#
# bucket notifications that trigger lambdas
# 

# lambda running in MJMM account but invoked from EE account
data "aws_lambda_function" "getextraorbitfiles" {
#  provider      = aws.mjmmacct
  function_name = "getExtraOrbitFilesV2"
}

data "aws_lambda_function" "ftptoukmdalambda" {
  function_name = "ftpToUkmon"
}

resource "aws_s3_bucket_notification" "ukmdashared_notification" {
  bucket = aws_s3_bucket.ukmdashared.id
  lambda_function {
    lambda_function_arn = data.aws_lambda_function.getextraorbitfiles.arn
    id                  = "pickles"
    events = [
      "s3:ObjectCreated:*"
    ]
    filter_prefix = "matches/RMSCorrelate/trajectories"
    filter_suffix = ".pickle"
  }

  lambda_function {
    lambda_function_arn = data.aws_lambda_function.ftptoukmdalambda.arn
    id                  = "ftptoukmda"
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "matches/RMSCorrelate/"
    filter_suffix       = ".txt"
  }

  #lambda_function {
  #  lambda_function_arn = aws_lambda_function.imgreplicatelambda.arn
  #  id                  = "synctoukmon"
  #  events              = ["s3:ObjectCreated:*"]
  #  filter_prefix       = "archive/"
  #}

}

resource "aws_lambda_permission" "permgetextraorbfileslambda" {
  statement_id   = "AllowExecutionFromS3Bucket"
  action         = "lambda:InvokeFunction"
  function_name  = data.aws_lambda_function.getextraorbitfiles.arn
  principal      = "s3.amazonaws.com"
  source_account = data.aws_caller_identity.current.account_id
  source_arn     = aws_s3_bucket.ukmdashared.arn
}

resource "aws_lambda_permission" "permftptoukmdalambda" {
  statement_id   = "AllowExecutionFromS3Bucket"
  action         = "lambda:InvokeFunction"
  function_name  = data.aws_lambda_function.ftptoukmdalambda.arn
  principal      = "s3.amazonaws.com"
  source_account = data.aws_caller_identity.current.account_id
  source_arn     = aws_s3_bucket.ukmdashared.arn
}

#resource "aws_lambda_permission" "permarcreplicatelambda" {
#  statement_id   = "AllowExecutionFromShrBucket"
#  action         = "lambda:InvokeFunction"
#  function_name  = aws_lambda_function.imgreplicatelambda.arn
#  principal      = "s3.amazonaws.com"
#  source_account = data.aws_caller_identity.current.account_id
#  source_arn     = aws_s3_bucket.ukmdashared.arn
#}
