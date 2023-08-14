##############################################################################
# Copyright (c) 2018- Mark McIntyre
##############################################################################
locals {
  origin_id = "S3-cf-templates-rvcg0s5ddz85-eu-west-2"
}

resource "aws_cloudfront_distribution" "arch_distribution" {
  origin {
    connection_attempts = 3
    connection_timeout  = 10
    domain_name         = aws_s3_bucket.archsite.bucket_domain_name
    origin_id           = local.origin_id
    s3_origin_config {
      origin_access_identity = "origin-access-identity/cloudfront/${aws_cloudfront_origin_access_identity.archsite_oaid.id}"
    }
  }
  aliases             = ["archive.ukmeteornetwork.co.uk", ]
  comment             = "ukmeteornetwork archive site"
  default_root_object = "index.html"
  is_ipv6_enabled     = true
  enabled             = true
  restrictions {
    geo_restriction {
      restriction_type = "none"
      locations        = []
    }
  }
  default_cache_behavior {
    # Using the CachingDisabled managed policy ID:
    cache_policy_id = "4135ea2d-6df8-44a3-9df3-4b5a84be39ad"
    compress        = true
    allowed_methods = [
      "GET",
      "DELETE",
      "OPTIONS",
      "PATCH",
      "POST",
      "PUT",
    "HEAD"]
    target_origin_id       = local.origin_id
    viewer_protocol_policy = "redirect-to-https"
    cached_methods         = ["GET", "HEAD"]
  }
  viewer_certificate {
    acm_certificate_arn            = aws_acm_certificate.ukmeteornetworkcert.arn
    cloudfront_default_certificate = false
    minimum_protocol_version       = "TLSv1.2_2021"
    ssl_support_method             = "sni-only"
  }
  logging_config {
    bucket          = "ukmon-s3-access-logs.s3.amazonaws.com"
    include_cookies = false
    prefix          = "cdn"
  }
  tags = {
    "billingtag" = "ukmon"
  }
}

resource "aws_cloudfront_origin_access_identity" "archsite_oaid" {
  comment = "access-identity-ukmonarchive"
}

output "cfdistro_url" {
  value = aws_cloudfront_distribution.arch_distribution.domain_name
}

