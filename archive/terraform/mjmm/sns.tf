# Copyright (C) 2018-2023 Mark McIntyre

#
# SNS for notifications
#

resource "aws_sns_topic" "ukmonalerts" {
  name         = "EBSActivit"
  display_name = "DiskspaceMonitoring"
  tags = {
    billingtag = "ukmon"
  }
}

resource "aws_sns_topic_subscription" "ukmonsubs" {
  topic_arn                       = aws_sns_topic.ukmonalerts.arn
  protocol                        = "email"
  endpoint                        = "markmcintyre99@googlemail.com"
  confirmation_timeout_in_minutes = 1
  endpoint_auto_confirms          = false
}
