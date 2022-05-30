#
# bucket notifications that trigger lambdas
# 

resource "aws_s3_bucket_notification" "ukmonshared_notification" {
  bucket = aws_s3_bucket.ukmonshared.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.consolidatejpgslambda.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "archive/"
    filter_suffix       = ".jpg"
  }

  lambda_function {
    lambda_function_arn = aws_lambda_function.ftpdetectlambda.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "archive/"
    filter_suffix       = ".txt"
  }

  lambda_function {
    lambda_function_arn = aws_lambda_function.consolidatelatestlambda.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "archive/"
    filter_suffix       = ".png"
  }
  lambda_function {
    lambda_function_arn = aws_lambda_function.consolidatekmlslambda.arn
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
}
