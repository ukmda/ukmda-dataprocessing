# Copyright (C) 2018-2023 Mark McIntyre
#
# bucket notifications that trigger lambdas
# 

resource "aws_s3_bucket_notification" "ukmda_live_notification" {
  bucket = aws_s3_bucket.ukmdalive.id
  provider         = aws.eu-west-1-prov
  lambda_function {
    lambda_function_arn = aws_lambda_function.copylivelambda.arn
    id                  = "allfiles"
    events = [
      "s3:ObjectCreated:*"
    ]
    filter_suffix       = ".jpg"
  }
}
