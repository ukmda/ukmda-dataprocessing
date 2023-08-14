##############################################################################
# Copyright (c) 2018- Mark McIntyre
##############################################################################
# terraform to create the dynamodb tables

resource "aws_dynamodb_table" "live_bright_table" {
  name         = "LiveBrightness"
  billing_mode = "PAY_PER_REQUEST"
  #read_capacity  = 20
  #write_capacity = 20
  hash_key  = "CaptureNight"
  range_key = "Timestamp"

  attribute {
    name = "CaptureNight"
    type = "N"
  }

  attribute {
    name = "Timestamp"
    type = "N"
  }

  attribute {
    name = "camid"
    type = "S"
  }

  global_secondary_index {
    hash_key           = "camid"
    name               = "camid-CaptureNight-index"
    non_key_attributes = []
    projection_type    = "ALL"
    range_key          = "CaptureNight"
    read_capacity      = 0
    write_capacity     = 0
  }
  ttl {
    attribute_name = "ExpiryDate"
    enabled        = true
  }
  tags = {
    Name       = "LiveBrightness"
    billingtag = "ukmon"
  }
}

resource "aws_dynamodb_table" "camera_table" {
  name         = "ukmon_camdetails"
  billing_mode = "PAY_PER_REQUEST"
  #read_capacity  = 20
  #write_capacity = 20
  hash_key  = "stationid"
  range_key = "site"
  provider  = aws.eu-west-1-prov

  attribute {
    name = "stationid"
    type = "S"
  }

  attribute {
    name = "site"
    type = "S"
  }

  #ttl {
  #  attribute_name = "ExpiryDate"
  #  enabled        = true
  #}
  tags = {
    Name       = "ukmon_camdetails"
    billingtag = "ukmon"
  }
}


resource "aws_dynamodb_table" "uploadtimes_table" {
  name         = "ukmon_uploadtimes"
  billing_mode = "PAY_PER_REQUEST"
  #read_capacity  = 20
  #write_capacity = 20
  hash_key  = "stationid"
  range_key = "dtstamp"
  provider  = aws.eu-west-1-prov

  attribute {
    name = "stationid"
    type = "S"
  }

  attribute {
    name = "dtstamp"
    type = "S"
  }

  attribute {
    name = "uploaddate"
    type = "N"
  }

  global_secondary_index {
    name            = "uploaddate-stationid-index"
    hash_key        = "uploaddate"
    range_key       = "stationid"
    projection_type = "ALL"
  }
  ttl {
    attribute_name = "ExpiryDate"
    enabled        = true
  }
  tags = {
    Name       = "ukmon_uploadtimes"
    billingtag = "ukmon"
  }
}

resource "aws_dynamodb_table" "live_table" {
  name         = "live"
  billing_mode = "PAY_PER_REQUEST"
  provider     = aws.eu-west-1-prov

  hash_key  = "image_name"
  range_key = "timestamp"

  attribute {
    name = "image_name"
    type = "S"
  }
  attribute {
    name = "timestamp"
    type = "S"
  }
  attribute {
    name = "image_timestamp"
    type = "S"
  }
  attribute {
    name = "year"
    type = "S"
  }
  attribute {
    name = "month"
    type = "S"
  }
  global_secondary_index {
    name               = "year-image_timestamp-index"
    hash_key           = "year"
    range_key          = "image_timestamp"
    projection_type    = "ALL"
    non_key_attributes = []
    read_capacity      = 0
    write_capacity     = 0
  }
  global_secondary_index {
    name               = "month-image_name-index"
    hash_key           = "month"
    range_key          = "image_name"
    projection_type    = "ALL"
    non_key_attributes = []
    read_capacity      = 0
    write_capacity     = 0
  }
  ttl {
    attribute_name = "expiry_date"
    enabled        = true
  }
  tags = {
    Name       = "live"
    billingtag = "ukmon"
  }
}
