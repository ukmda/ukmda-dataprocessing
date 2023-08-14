##############################################################################
# Copyright (c) 2018- Mark McIntyre
##############################################################################
# Route53 stuff for ukmon

resource "aws_route53_zone" "ukmeteornetwork" {
  name         = "ukmeteornetwork.co.uk"
  comment       = "Hosted zone for ukmeteornetwork.co.uk"
  tags = {
    billingtag = "ukmon"
    Project  = "www.ukmeteornetwork.co.uk"
  }
}

