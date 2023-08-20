# Copyright (C) 2018-2023 Mark McIntyre
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
      "SRCHBUCKET" = "${var.sharedbucket}"
    }
  }
  ephemeral_storage {
    size = 512
  }
  tags = {
    Name       = "matchDataApiHandler"
    billingtag = "ukmda"
  }
}

data "template_file" "match_body_templ" {
  template = file("files/matchApiJson/ukmdaMatchApi.json")
  vars = {
    thisacct = "${data.aws_caller_identity.current.account_id}"
  }
}


resource "aws_api_gateway_rest_api" "matchapi_apigateway" {
  body     = data.template_file.match_body_templ.rendered # file("files/matchApiJson/ukmdaMatchApi.json")
  name     = "ukmdaMatchApi"
  provider = aws.eu-west-1-prov
  endpoint_configuration {
    types = ["REGIONAL"]
  }
  tags = {
    Name       = "ukmdaMatchApi"
    billingtag = "ukmda"
  }
}

resource "aws_api_gateway_base_path_mapping" "matchapi" {
  api_id      = aws_api_gateway_rest_api.matchapi_apigateway.id
  stage_name  = "prod"
  domain_name = aws_api_gateway_domain_name.apigwdomain.domain_name
  base_path = "matches"
  provider                 = aws.eu-west-1-prov
  depends_on  = [aws_api_gateway_stage.matchapistage]
}

resource "aws_api_gateway_stage" "matchapistage" {
  deployment_id = aws_api_gateway_deployment.matchapi_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.matchapi_apigateway.id
  stage_name    = "prod"
  provider = aws.eu-west-1-prov
}

resource "aws_api_gateway_deployment" "matchapi_deployment" {
  rest_api_id = aws_api_gateway_rest_api.matchapi_apigateway.id
  provider = aws.eu-west-1-prov
  triggers = {
    redeployment = sha1(jsonencode(aws_api_gateway_rest_api.matchapi_apigateway.body))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_lambda_permission" "perm_apigw_match" {
  statement_id   = "AllowExecutionFromAPIGW"
  action         = "lambda:InvokeFunction"
  function_name  = aws_lambda_function.matchapilambda.arn
  principal      = "apigateway.amazonaws.com"
  source_arn     = "arn:aws:execute-api:eu-west-2:183798037734:975kbpqxg6/*/GET/"
  #source_arn     = "${aws_api_gateway_rest_api.matchapi_apigateway.arn}/*/*"
}
