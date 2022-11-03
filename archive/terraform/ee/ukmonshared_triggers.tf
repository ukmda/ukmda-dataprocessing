#
# bucket notifications that trigger lambdas
# 

resource "aws_s3_bucket_notification" "ukmonshared_notification" {
  bucket = aws_s3_bucket.ukmonshared.id

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
    events = [
      "s3:ObjectCreated:CompleteMultipartUpload",
      "s3:ObjectCreated:Post",
      "s3:ObjectCreated:Put"
    ]
    filter_prefix = "archive/"
    filter_suffix = ".csv"
  }
  lambda_function {
    lambda_function_arn = "arn:aws:lambda:eu-west-2:317976261112:function:getExtraOrbitFilesV2"
    id                  = "pickles"
    events = [
      "s3:ObjectCreated:*"
    ]
    filter_prefix = "matches/RMSCorrelate/trajectories"
    filter_suffix = ".pickle"
  }

  lambda_function {
    lambda_function_arn = aws_lambda_function.logcamuploadtimelambda.arn
    id                  = "LogCamUploadTime"
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "archive/"
    filter_suffix       = ".config"
  }
}

# lambda permissions to allow functions to be executed from S3
resource "aws_lambda_permission" "permconsolidatejpgslambda" {
  statement_id   = "AllowExecutionFromS3Bucket"
  action         = "lambda:InvokeFunction"
  function_name  = aws_lambda_function.consolidatejpgslambda.arn
  principal      = "s3.amazonaws.com"
  source_account = "822069317839"
  source_arn     = aws_s3_bucket.ukmonshared.arn
}
resource "aws_lambda_permission" "permftpdetectlambda" {
  statement_id   = "AllowExecutionFromS3Bucket"
  action         = "lambda:InvokeFunction"
  function_name  = aws_lambda_function.ftpdetectlambda.arn
  principal      = "s3.amazonaws.com"
  source_account = "822069317839"
  source_arn     = aws_s3_bucket.ukmonshared.arn
}
resource "aws_lambda_permission" "permconsolidatelatestlambda" {
  statement_id   = "AllowExecutionFromS3Bucket"
  action         = "lambda:InvokeFunction"
  function_name  = aws_lambda_function.consolidatelatestlambda.arn
  principal      = "s3.amazonaws.com"
  source_account = "822069317839"
  source_arn     = aws_s3_bucket.ukmonshared.arn
}
resource "aws_lambda_permission" "permconsolidatekmlslambda" {
  statement_id   = "AllowExecutionFromS3Bucket"
  action         = "lambda:InvokeFunction"
  function_name  = aws_lambda_function.consolidatekmlslambda.arn
  principal      = "s3.amazonaws.com"
  source_account = "822069317839"
  source_arn     = aws_s3_bucket.ukmonshared.arn
}
resource "aws_lambda_permission" "permcsvtriggerlambda" {
  statement_id   = "AllowExecutionFromS3Bucket"
  action         = "lambda:InvokeFunction"
  function_name  = aws_lambda_function.csvtriggerlambda.arn
  principal      = "s3.amazonaws.com"
  source_account = "822069317839"
  source_arn     = aws_s3_bucket.ukmonshared.arn
}


resource "aws_lambda_permission" "permloguploadlambda" {
  statement_id   = "AllowExecutionFromS3Bucket"
  action         = "lambda:InvokeFunction"
  function_name  = aws_lambda_function.logcamuploadtimelambda.arn
  principal      = "s3.amazonaws.com"
  source_account = "822069317839"
  source_arn     = aws_s3_bucket.ukmonshared.arn
}
