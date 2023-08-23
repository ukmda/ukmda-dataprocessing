data "archive_file" "imgreplicatezip" {
  type        = "zip"
  source_dir  = "${path.root}/files/imgReplicate/"
  output_path = "${path.root}/files/imgReplicate.zip"
}

resource "aws_lambda_function" "imgreplicatelambda" {
#  provider         = aws.eu-west-1-prov
  function_name    = "imgReplicate"
  description      = "replication of data between accounts"
  filename         = data.archive_file.imgreplicatezip.output_path
  source_code_hash = data.archive_file.imgreplicatezip.output_base64sha256
  handler          = "imgReplicate.lambda_handler"
  runtime          = "python3.8"
  memory_size      = 128
  timeout          = 300
  role             = aws_iam_role.lambda-s3-full-access-role.arn
  publish          = false
  environment {
    variables = {
      TARGWEBBUCKET="ukmeteornetworkarchive"
      TARGSHRBUCKET="ukmon-shared"
    }
  }
  tags = {
    Name        = "imgReplicate"
    billingtag  = "ukmda"
  }
}

