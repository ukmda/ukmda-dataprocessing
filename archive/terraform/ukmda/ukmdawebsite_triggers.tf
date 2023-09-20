# Copyright (C) 2018-2023 Mark McIntyre
#
# bucket notifications that trigger lambdas
# 

# lambda running in MJMM account but invoked from EE account
#data "aws_lambda_function" "imgreplicatelambda" {
#  function_name = "ImgReplicator"
#}

resource "aws_s3_bucket_notification" "ukmdaweb_notification" {
  bucket = var.websitebucket
  lambda_function {
    lambda_function_arn = aws_lambda_function.imgreplicatelambda.arn
    id                  = "imgReplicate"
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "img/single/"
    filter_suffix       = ".jpg"
  }
  lambda_function {
    lambda_function_arn = aws_lambda_function.imgreplicatelambda.arn
    id                  = "mp4Replicate"
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "img/mp4/"
    filter_suffix       = ".mp4"
  }
}

resource "aws_lambda_permission" "permimgreplicatelambda" {
  statement_id   = "AllowExecutionFromS3Bucket"
  action         = "lambda:InvokeFunction"
  function_name  = aws_lambda_function.imgreplicatelambda.arn
  principal      = "s3.amazonaws.com"
  source_account = data.aws_caller_identity.current.account_id
  source_arn     = aws_s3_bucket.archsite.arn
}
