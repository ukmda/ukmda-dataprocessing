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
/*
  lambda_function {
    lambda_function_arn = aws_lambda_function.consolidatejpgslambda.arn
    id                  = "jpgs"
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "archive/"
    filter_suffix       = ".jpg"
  }

  lambda_function {
    lambda_function_arn = aws_lambda_function.ftpdetectlambda.arn
    id                  = "ftpdetects"
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "archive/"
    filter_suffix       = ".txt"
  }

  lambda_function {
    lambda_function_arn = aws_lambda_function.consolidatelatestlambda.arn
    id                  = "pngs"
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "archive/"
    filter_suffix       = ".png"
  }
  lambda_function {
    lambda_function_arn = aws_lambda_function.consolidatekmlslambda.arn
    id                  = "kmls"
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "archive/"
    filter_suffix       = ".kml"
  }
  lambda_function {
    lambda_function_arn = aws_lambda_function.csvtriggerlambda.arn
    id                  = "CSVTrigger"
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "archive/"
    filter_suffix       = ".csv"
  }
  */
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

}

# lambda permissions to allow functions to be executed from S3
resource "aws_lambda_permission" "permconsolidatejpgslambda" {
  statement_id   = "AllowExecutionFromS3Bucket"
  action         = "lambda:InvokeFunction"
  function_name  = aws_lambda_function.consolidatejpgslambda.arn
  principal      = "s3.amazonaws.com"
  source_account = data.aws_caller_identity.current.account_id
  source_arn     = aws_s3_bucket.ukmdashared.arn
}

resource "aws_lambda_permission" "permftpdetectlambda" {
  statement_id   = "AllowExecutionFromS3Bucket"
  action         = "lambda:InvokeFunction"
  function_name  = aws_lambda_function.ftpdetectlambda.arn
  principal      = "s3.amazonaws.com"
  source_account = data.aws_caller_identity.current.account_id
  source_arn     = aws_s3_bucket.ukmdashared.arn
}

resource "aws_lambda_permission" "permconsolidatelatestlambda" {
  statement_id   = "AllowExecutionFromS3Bucket"
  action         = "lambda:InvokeFunction"
  function_name  = aws_lambda_function.consolidatelatestlambda.arn
  principal      = "s3.amazonaws.com"
  source_account = data.aws_caller_identity.current.account_id
  source_arn     = aws_s3_bucket.ukmdashared.arn
}

resource "aws_lambda_permission" "permconsolidatekmlslambda" {
  statement_id   = "AllowExecutionFromS3Bucket"
  action         = "lambda:InvokeFunction"
  function_name  = aws_lambda_function.consolidatekmlslambda.arn
  principal      = "s3.amazonaws.com"
  source_account = data.aws_caller_identity.current.account_id
  source_arn     = aws_s3_bucket.ukmdashared.arn
}

resource "aws_lambda_permission" "permcsvtriggerlambda" {
  statement_id   = "AllowExecutionFromS3Bucket"
  action         = "lambda:InvokeFunction"
  function_name  = aws_lambda_function.csvtriggerlambda.arn
  principal      = "s3.amazonaws.com"
  source_account = data.aws_caller_identity.current.account_id
  source_arn     = aws_s3_bucket.ukmdashared.arn
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
