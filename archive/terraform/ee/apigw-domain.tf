##############################################################################
# Copyright (c) 2018- Mark McIntyre
##############################################################################
# domain name to be used by APIs 
resource "aws_api_gateway_domain_name" "apigwdomain" {
  regional_certificate_arn = aws_acm_certificate_validation.apicert.certificate_arn
  domain_name              = aws_acm_certificate.apicert.domain_name
  provider                 = aws.eu-west-1-prov
}

# DNS entry for the api domain
resource "aws_route53_record" "apidnsentry" {
  name    = aws_api_gateway_domain_name.apigwdomain.domain_name
  type    = "A"
  zone_id = aws_route53_zone.ukmeteornetwork.id

  alias {
    evaluate_target_health = true
    name                   = aws_api_gateway_domain_name.apigwdomain.regional_domain_name
    zone_id                = aws_api_gateway_domain_name.apigwdomain.regional_zone_id
  }
}

resource "aws_api_gateway_base_path_mapping" "matchapi" {
  api_id      = aws_api_gateway_rest_api.matchapi_apigateway.id
  stage_name  = "prod"
  domain_name = aws_api_gateway_domain_name.apigwdomain.domain_name
  base_path = "matches"
  provider                 = aws.eu-west-1-prov
}

# apis managed by SAM need to be delared as data sources
data "aws_api_gateway_rest_api" "fetchECSVapi" {
  name = "fetchECSV"
  provider                 = aws.eu-west-1-prov
}

data "aws_api_gateway_rest_api" "matchpickleapi" {
  name = "matchPickleApi"
  provider                 = aws.eu-west-1-prov
}

resource "aws_api_gateway_base_path_mapping" "ecsvapi" {
  api_id      = data.aws_api_gateway_rest_api.fetchECSVapi.id
  stage_name  = "Prod"
  domain_name = aws_api_gateway_domain_name.apigwdomain.domain_name
  base_path = ""
  provider                 = aws.eu-west-1-prov
}

resource "aws_api_gateway_base_path_mapping" "pickleapi" {
  api_id      = data.aws_api_gateway_rest_api.matchpickleapi.id
  stage_name  = "Prod"
  domain_name = aws_api_gateway_domain_name.apigwdomain.domain_name
  base_path = "pickle"
  provider                 = aws.eu-west-1-prov
}
