# Copyright (C) 2018-2023 Mark McIntyre
#
# SNS for notifications
#

resource "aws_sns_topic" "ukmdaalerts" {
  name         = "ukmdaAlerting"
  display_name = "DiskspaceMonitoring"
  tags = {
    billingtag = "ukmda"
  }
}

resource "aws_sns_topic_subscription" "ukmdasubs" {
  topic_arn                       = aws_sns_topic.ukmdaalerts.arn
  protocol                        = "email"
  endpoint                        = "markmcintyre99@googlemail.com"
  confirmation_timeout_in_minutes = 5
  endpoint_auto_confirms          = false
}
