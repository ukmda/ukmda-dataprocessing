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
    name               = "uploaddate-stationid-index"
    hash_key           = "uploaddate"
    range_key          = "stationid"
    projection_type    = "ALL"
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
