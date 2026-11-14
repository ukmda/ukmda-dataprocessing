# Copyright (C) 2018-2023 Mark McIntyre
# Route53 stuff for ukmda

resource "aws_route53_zone" "ukmeteors" {
  name         = var.domain_name
  comment       = "Hosted zone for ukmeteors.co.uk"
  tags = {
    billingtag = "ukmda"
    Project  = "www.ukmeteors.co.uk"
  }
}

#########################################################################
# Other domains we own, redirecting via the Batch server to our main site
# See docs/OWNEDDOMAINS.md for how this is all configured

resource "aws_route53_zone" "ukmeteornetwork_com" {
  name         = "ukmeteornetwork.com"
  comment       = "Hosted zone for ukmeteornetwork.com"
  tags = {
    billingtag = "ukmda"
    Project  = "ukmeteornetwork.com"
  }
}

# DNS entry for www.ukmeteornetwork.com
resource "aws_route53_record" "www_ukmeteornetwork_com" {
  name    = "www.ukmeteornetwork.com"
  type    = "A"
  zone_id = aws_route53_zone.ukmeteornetwork_com.id
  ttl     = 300
  records = [aws_eip.batchserver.public_ip]
}
resource "aws_route53_record" "ukmeteornetwork_com" {
  name    = "ukmeteornetwork.com"
  type    = "A"
  zone_id = aws_route53_zone.ukmeteornetwork_com.id
  ttl     = 300
  records = [aws_eip.batchserver.public_ip]
}
