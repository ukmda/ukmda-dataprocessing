#
# terraform to create the lambdas in the MJMM account
#

# the Lambda's body is being uploaded via a Zip file
# this block creates a zip file from the contents of files/src
data "archive_file" "consolidatejpgszip" {
  type        = "zip"
  source_dir  = "${path.root}/files/consolidateJpgs/"
  output_path = "${path.root}/files/consolidateJpgs.zip"
}

resource "aws_lambda_function" "consolidatejpgslambda" {
  function_name    = "consolidateJpgs"
  description      = "Copies new jpgs from the archive upload area to the website"
  filename         = data.archive_file.consolidatejpgszip.output_path
  source_code_hash = data.archive_file.consolidatejpgszip.output_base64sha256
  handler          = "consolidateJpgs.lambda_handler"
  runtime          = "python3.8"
  memory_size      = 128
  timeout          = 60
  role             = aws_iam_role.S3FullAccess.arn
  publish          = false
  environment {
    variables = {
      "WEBSITEBUCKET" = "s3://ukmeteornetworkarchive"
    }
  }
  ephemeral_storage {
    size = 512
  }
  tags = {
    Name       = "consolidateJpgs"
    billingtag = "ukmon"
  }
}

# consolidateKmls
data "archive_file" "consolidatekmlszip" {
  type        = "zip"
  source_dir  = "${path.root}/files/consolidateKmls/"
  output_path = "${path.root}/files/consolidateKmls.zip"
}

resource "aws_lambda_function" "consolidatekmlslambda" {
  function_name    = "consolidateKmls"
  description      = "Copies kml files to the website for map drawing"
  filename         = data.archive_file.consolidatekmlszip.output_path
  source_code_hash = data.archive_file.consolidatekmlszip.output_base64sha256
  handler          = "consolidateKmls.lambda_handler"
  runtime          = "python3.8"
  memory_size      = 128
  timeout          = 60
  role             = aws_iam_role.S3FullAccess.arn
  publish          = false
  environment {
    variables = {
      "WEBSITEBUCKET" = "s3://ukmeteornetworkarchive"
    }
  }
  ephemeral_storage {
    size = 512
  }
  tags = {
    Name       = "consolidateKmls"
    billingtag = "ukmon"
  }
}

# consolidateLatest - consolidates individual station PNGs and JPGs for the station 
# status page 
data "archive_file" "consolidatelatestzip" {
  type        = "zip"
  source_dir  = "${path.root}/files/consolidateLatest/"
  output_path = "${path.root}/files/consolidateLatest.zip"
}

resource "aws_lambda_function" "consolidatelatestlambda" {
  function_name    = "consolidateLatest"
  description      = "consolidate the radiant map PNGs onto the website"
  filename         = data.archive_file.consolidatelatestzip.output_path
  source_code_hash = data.archive_file.consolidatelatestzip.output_base64sha256
  handler          = "consolidateLatest.lambda_handler"
  runtime          = "python3.8"
  memory_size      = 128
  timeout          = 60
  role             = aws_iam_role.S3FullAccess.arn
  publish          = false
  environment {
    variables = {
      "WEBSITEBUCKET" = "s3://ukmeteornetworkarchive"
    }
  }
  ephemeral_storage {
    size = 512
  }
  tags = {
    Name       = "consolidateLatest"
    billingtag = "ukmon"
  }
}

# csvTrigger - consolidate CSV files for the old-style analysis. Not sure this is still needed. 
data "archive_file" "csvtriggerzip" {
  type        = "zip"
  source_dir  = "${path.root}/files/csvTrigger/"
  output_path = "${path.root}/files/csvTrigger.zip"
}

resource "aws_lambda_function" "csvtriggerlambda" {
  function_name    = "CSVTrigger"
  description      = "Copies the camera CSV files to the temp area for later consolidation."
  filename         = data.archive_file.csvtriggerzip.output_path
  source_code_hash = data.archive_file.csvtriggerzip.output_base64sha256
  handler          = "csvTrigger.lambda_handler"
  runtime          = "python3.8"
  memory_size      = 128
  timeout          = 90
  role             = aws_iam_role.S3FullAccess.arn
  publish          = false
  ephemeral_storage {
    size = 512
  }
  tags = {
    Name       = "CSVTrigger"
    billingtag = "ukmon"
  }
}

# csvTrigger - Consolidates RMS FTPdetect files for correlation and trajectory solving
data "archive_file" "ftpdetectzip" {
  type        = "zip"
  source_dir  = "${path.root}/files/consolidateFTPdetect/"
  output_path = "${path.root}/files/consolidateFTPdetect.zip"
}

resource "aws_lambda_function" "ftpdetectlambda" {
  function_name    = "consolidateFTPdetect"
  description      = "Consolidates FTPdetect files for correlation and trajectory solving"
  filename         = data.archive_file.ftpdetectzip.output_path
  source_code_hash = data.archive_file.ftpdetectzip.output_base64sha256
  handler          = "consolidateFTPdetect.lambda_handler"
  runtime          = "python3.8"
  memory_size      = 128
  timeout          = 30
  role             = aws_iam_role.S3FullAccess.arn
  publish          = false
  ephemeral_storage {
    size = 512
  }
  tags = {
    Name       = "consolidateFTPdetect"
    billingtag = "ukmon"
  }
}
