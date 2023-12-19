# Copyright (C) 2018-2023 Mark McIntyre

#
# Cloudwatch alarms etc
#
/*
resource "aws_cloudwatch_metric_alarm" "ukmonhelperDiskSpace" {
  alarm_name                = "ukmonHelperDiskspace"
  comparison_operator       = "GreaterThanThreshold"
  evaluation_periods        = "1"
  metric_name               = "disk_used_percent"
  namespace                 = "CWAgent"
  period                    = "300"
  statistic                 = "Average"
  threshold                 = "90"
  alarm_description         = "ukmonhelper diskspace exceeds 90pct"
  insufficient_data_actions = []
  datapoints_to_alarm       = 1
  alarm_actions             = [aws_sns_topic.ukmonalerts.arn, ]
  dimensions = {
    "ImageId"      = aws_instance.ukmonhelper_g.ami
    "InstanceId"   = aws_instance.ukmonhelper_g.id
    "InstanceType" = aws_instance.ukmonhelper_g.instance_type
    "device"       = "nvme0n1p1"
    "fstype"       = "xfs"
    "path"         = "/"
  }
  tags = {
    "billingtag" = "ukmon"
  }
}
*/