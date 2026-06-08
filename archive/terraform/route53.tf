# Copyright (C) 2018-2023 Mark McIntyre
# Route53 stuff for ukmda

resource "aws_route53_zone" "ukmeteors" {
  name         = "ukmeteors.co.uk"
  comment       = "Hosted zone for ukmeteors.co.uk"
  tags = {
    billingtag = "ukmda"
    Project  = "www.ukmeteors.co.uk"
  }
}

