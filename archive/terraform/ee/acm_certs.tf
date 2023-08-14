##############################################################################
# Copyright (c) 2018- Mark McIntyre
##############################################################################
# ACM certificates for main domain name
resource "aws_acm_certificate" "ukmeteornetworkcert" {
  domain_name   = "*.ukmeteornetwork.co.uk"
  provider = aws.us-east-1-prov
  validation_method = "DNS"
  tags = {
    billingtag = "ukmon"
  }
  lifecycle {
    create_before_destroy = true
  }
}
/* commented out till needed
resource "aws_acm_certificate_validation" "maincert" {
  certificate_arn         = aws_acm_certificate.ukmeteornetworkcert.arn
  validation_record_fqdns = [for record in aws_route53_record.ukmeteornetwork_main: record.fqdn]
  provider                = aws.eu-west-1-prov
}

#Route 53 record in the hosted zone to validate the Certificate
resource "aws_route53_record" "ukmeteornetwork_main" {
  zone_id = aws_route53_zone.ukmeteornetwork.zone_id
  for_each = {
    for dvo in aws_acm_certificate.ukmeteornetworkcert.domain_validation_options : dvo.domain_name => {
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
*/

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

