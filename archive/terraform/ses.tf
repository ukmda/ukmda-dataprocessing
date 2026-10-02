# Copyright (C) 2018- Mark McIntyre

resource "aws_ses_domain_identity" "ukmeteors" {
  domain = var.domain_name
}

# ses mail records
resource "aws_route53_record" "ukmda_mx_records" {
  zone_id = aws_route53_zone.ukmeteors.id
  name    = var.domain_name
  type    = "MX"
  ttl     = "600"

  records = [
    "10 inbound-smtp.eu-west-2.amazonses.com",
    "10 inbound-smtp.eu-west-2.amazonaws.com",
  ]
}

resource "aws_route53_record" "ukmeteors_amazonses_verification_record" {
  zone_id = aws_route53_zone.ukmeteors.zone_id
  name    = "_amazonses.ukmeteors.co.uk"
  type    = "TXT"
  ttl     = "600"
  records = [aws_ses_domain_identity.ukmeteors.verification_token]
}

resource "aws_ses_domain_dkim" "ukmeteors" {
  domain = aws_ses_domain_identity.ukmeteors.domain
}

resource "aws_route53_record" "ukmeteors_amazonses_dkim_record" {
  count   = 3
  zone_id = aws_route53_zone.ukmeteors.zone_id
  name    = "${aws_ses_domain_dkim.ukmeteors.dkim_tokens[count.index]}._domainkey"
  type    = "CNAME"
  ttl     = "600"
  records = ["${aws_ses_domain_dkim.ukmeteors.dkim_tokens[count.index]}.dkim.amazonses.com"]
}

resource "aws_ses_email_identity" "example" {
  email = "markmcintyre99@googlemail.com"
}