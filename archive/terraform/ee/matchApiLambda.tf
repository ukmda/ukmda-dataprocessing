# Lambda for the Match data API. Need to rework this. 
#
data "archive_file" "matchapizip" {
  type        = "zip"
  source_dir  = "${path.root}/files/matchDataApi/"
  output_path = "${path.root}/files/matchDataApi.zip"
}

resource "aws_lambda_function" "matchapilambda" {
  function_name    = "matchDataApiHandler"
  description      = "API to retrieve match event data"
  filename         = data.archive_file.matchapizip.output_path
  source_code_hash = data.archive_file.matchapizip.output_base64sha256
  handler          = "matchDataApiHandler.lambda_handler"
  runtime          = "python3.9"
  memory_size      = 128
  timeout          = 30
  role             = aws_iam_role.S3FullAccess.arn
  publish          = false
  environment {
    variables = {
      "SRCHBUCKET" = "ukmon-shared"
    }
  }
  ephemeral_storage {
    size = 512
  }
  tags = {
    Name       = "matchDataApiHandler"
    billingtag = "ukmon"
  }
}

/*

resource "aws_api_gateway_rest_api" "matchapi_apig" {
  body = jsonencode({
    openapi = "3.0.1"
    info = {
      title   = "example"
      version = "1.0"
    }
    paths = {
      "/path1" = {
        get = {
          x-amazon-apigateway-integration = {
            httpMethod           = "GET"
            payloadFormatVersion = "1.0"
            type                 = "HTTP_PROXY"
            uri                  = "https://ip-ranges.amazonaws.com/ip-ranges.json"
          }
        }
      }
    }
  })

  name = "example"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}
*/
