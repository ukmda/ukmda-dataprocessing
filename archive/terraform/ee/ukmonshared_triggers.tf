##############################################################################
# Copyright (c) 2018- Mark McIntyre
##############################################################################
#
# bucket notifications that trigger lambdas
# 

# lambda running in MJMM account but invoked from EE account
data "aws_lambda_function" "getextraorbitfiles" {
#  provider      = aws.mjmmacct
  function_name = "getExtraOrbitFilesV2"
}

resource "aws_s3_bucket_notification" "ukmonshared_notification" {
  bucket = aws_s3_bucket.ukmonshared.id

  lambda_function {
    lambda_function_arn = data.aws_lambda_function.getextraorbitfiles.arn
    id                  = "pickles"
    events = [
      "s3:ObjectCreated:*"
    ]
    filter_prefix = "matches/RMSCorrelate/trajectories"
    filter_suffix = ".pickle"
  }
}
