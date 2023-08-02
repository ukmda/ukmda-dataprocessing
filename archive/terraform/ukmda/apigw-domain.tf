# Copyright (C) 2018-2023 Mark McIntyre

# domain name to be used by APIs 
resource "aws_api_gateway_domain_name" "apigwdomain" {
  certificate_arn          = aws_acm_certificate_validation.apicert.certificate_arn
  domain_name              = aws_acm_certificate.apicert.domain_name
  provider                 = aws.eu-west-1-prov
  #endpoint_configuration  { types = ["REGIONAL"]  }
}


# DNS entry for the api domain
resource "aws_route53_record" "apidnsentry" {
  name    = aws_api_gateway_domain_name.apigwdomain.domain_name
  type    = "A"
  zone_id = aws_route53_zone.ukmeteors.id
  depends_on = [aws_api_gateway_domain_name.apigwdomain]
  
  alias {
    evaluate_target_health = true
    name                   = aws_api_gateway_domain_name.apigwdomain.cloudfront_domain_name
    zone_id                = aws_api_gateway_domain_name.apigwdomain.cloudfront_zone_id
  }
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

data "aws_api_gateway_rest_api" "liveimagesapi" {
  name = "getLiveImages"
  provider                 = aws.eu-west-1-prov
}

data "aws_api_gateway_rest_api" "fbdataapi" {
  name = "getFireballFiles"
  provider                 = aws.eu-west-1-prov
}

data "aws_api_gateway_rest_api" "searchapi" {
  name = "searchArchive"
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

resource "aws_api_gateway_base_path_mapping" "liveimgapi" {
  api_id      = data.aws_api_gateway_rest_api.liveimagesapi.id
  stage_name  = "Prod"
  domain_name = aws_api_gateway_domain_name.apigwdomain.domain_name
  base_path = "liveimages"
  provider                 = aws.eu-west-1-prov
}

resource "aws_api_gateway_base_path_mapping" "fbdataapi" {
  api_id      = data.aws_api_gateway_rest_api.fbdataapi.id
  stage_name  = "Prod"
  domain_name = aws_api_gateway_domain_name.apigwdomain.domain_name
  base_path = "fireballs"
  provider                 = aws.eu-west-1-prov
}

resource "aws_api_gateway_base_path_mapping" "searchapi" {
  api_id      = data.aws_api_gateway_rest_api.searchapi.id
  stage_name  = "Prod"
  domain_name = aws_api_gateway_domain_name.apigwdomain.domain_name
  base_path = "detections"
  provider                 = aws.eu-west-1-prov
}
