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
  endpoint                        = "mark.jm.mcintyre@cesmail.net"
  confirmation_timeout_in_minutes = 1
  endpoint_auto_confirms          = false
}