# terraform to create the dynamodb tables

resource "aws_dynamodb_table" "live_bright_table" {
  name           = "LiveBrightness"
  billing_mode   = "PAY_PER_REQUEST"
  #read_capacity  = 20
  #write_capacity = 20
  hash_key       = "CaptureNight"
  range_key      = "Timestamp"

  attribute {
    name = "CaptureNight"
    type = "N"
  }

  attribute {
    name = "Timestamp"
    type = "N"
  }

#  ttl {
#    attribute_name = "TimeToExist"
#    enabled        = false
#  }
/*
  global_secondary_index {
    name               = "GameTitleIndex"
    hash_key           = "GameTitle"
    range_key          = "TopScore"
    write_capacity     = 10
    read_capacity      = 10
    projection_type    = "INCLUDE"
    non_key_attributes = ["UserId"]
  }
*/
  tags = {
    Name        = "LiveBrightness"
    billingtag = "ukmon"
  }
}