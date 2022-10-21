# ACM certificates for API Gateway domain name

resource "aws_acm_certificate" "apicert" {
  domain_name       = "api.ukmeteornetwork.co.uk"
  validation_method = "DNS"
  provider          = aws.eu-west-1-prov

  tags = {
    billingtag = "ukmon"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_acm_certificate_validation" "apicert" {
  certificate_arn         = aws_acm_certificate.apicert.arn
  validation_record_fqdns = [for record in aws_route53_record.ukmeteornetwork_api : record.fqdn]
  provider                = aws.eu-west-1-prov
}

#Route 53 record in the hosted zone to validate the Certificate
resource "aws_route53_record" "ukmeteornetwork_api" {
  zone_id = aws_route53_zone.ukmeteornetwork.zone_id
  for_each = {
    for dvo in aws_acm_certificate.apicert.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 300
  type            = each.value.type
}

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
