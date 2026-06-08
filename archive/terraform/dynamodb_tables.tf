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
    name               = "camid-CaptureNight-index"
    non_key_attributes = []
    projection_type    = "ALL"
    read_capacity      = 0
    write_capacity     = 0
    key_schema {
      attribute_name = "camid"
      key_type       = "HASH"
    }
    key_schema {
      attribute_name = "CaptureNight"
      key_type       = "RANGE"
    }
  }
  ttl {
    attribute_name = "ExpiryDate"
    enabled        = true
  }
  tags = {
    Name       = "LiveBrightness"
    billingtag = "ukmda"
  }
}

resource "aws_dynamodb_table" "camera_table" {
  name         = "camdetails"
  billing_mode = "PAY_PER_REQUEST"
  #read_capacity  = 20
  #write_capacity = 20
  hash_key  = "stationid"
  range_key = "site"
  #  provider  = aws.eu-west-1-prov

  attribute {
    name = "stationid"
    type = "S"
  }

  attribute {
    name = "site"
    type = "S"
  }
  global_secondary_index {
    name               = "site-stationid-index"
    non_key_attributes = []
    projection_type    = "ALL"
    read_capacity      = 0
    write_capacity     = 0
    key_schema {
      attribute_name = "site"
      key_type       = "HASH"
    }
    key_schema {
      attribute_name = "stationid"
      key_type       = "RANGE"
    }
  }
  tags = {
    Name       = "camdetails"
    billingtag = "ukmda"
  }
}


resource "aws_dynamodb_table" "uploadtimes_table" {
  name         = "uploadtimes"
  billing_mode = "PAY_PER_REQUEST"
  #read_capacity  = 20
  #write_capacity = 20
  hash_key  = "stationid"
  range_key = "dtstamp"
  #provider  = aws.eu-west-1-prov

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
    projection_type = "ALL"
    key_schema {
      attribute_name = "uploaddate"
      key_type       = "HASH"
    }
    key_schema {
      attribute_name = "stationid"
      key_type       = "RANGE"
    }
  }
  ttl {
    attribute_name = "ExpiryDate"
    enabled        = true
  }
  tags = {
    Name       = "uploadtimes"
    billingtag = "ukmda"
  }
}

resource "aws_dynamodb_table" "live_table" {
  name         = "live"
  billing_mode = "PAY_PER_REQUEST"
  #  provider     = aws.eu-west-1-prov

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
    projection_type    = "ALL"
    non_key_attributes = []
    read_capacity      = 0
    write_capacity     = 0
    key_schema {
      attribute_name = "year"
      key_type       = "HASH"
    }
    key_schema {
      attribute_name = "image_timestamp"
      key_type       = "RANGE"
    }

  }
  global_secondary_index {
    name               = "month-image_name-index"
    projection_type    = "ALL"
    non_key_attributes = []
    read_capacity      = 0
    write_capacity     = 0
    key_schema {
      attribute_name = "month"
      key_type       = "HASH"
    }
    key_schema {
      attribute_name = "image_name"
      key_type       = "RANGE"
    }
  }
  ttl {
    attribute_name = "expirydate"
    enabled        = true
  }
  tags = {
    Name       = "live"
    billingtag = "ukmda"
  }
}
