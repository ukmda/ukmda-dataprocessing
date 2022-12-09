#
# Cloudwatch alarms etc
#

resource "aws_cloudwatch_metric_alarm" "calcServerDiskSpace" {
  alarm_name                = "CalcServer diskspace"
  comparison_operator       = "GreaterThanThreshold"
  evaluation_periods        = "1"
  metric_name               = "disk_used_percent"
  namespace                 = "CWAgent"
  period                    = "300"
  statistic                 = "Average"
  threshold                 = "90"
  alarm_description         = "CalcServer diskspace has gone over 90%"
  insufficient_data_actions = []
  datapoints_to_alarm       = 1
  alarm_actions             = [aws_sns_topic.ukmonalerts.arn, ]
  dimensions = {
    "ImageId"      = aws_instance.CalcEngine4ARM.ami
    "InstanceId"   = aws_instance.CalcEngine4ARM.id
    "InstanceType" = aws_instance.CalcEngine4ARM.instance_type
    "device"       = "nvme0n1p1"
    "fstype"       = "xfs"
    "path"         = "/"
  }
  tags = {
    "billingtag" = "ukmon"
  }
}

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
    "ImageId"      = aws_instance.ukmonhelper.ami
    "InstanceId"   = aws_instance.ukmonhelper.id
    "InstanceType" = aws_instance.ukmonhelper.instance_type
    "device"       = "nvme0n1p1"
    "fstype"       = "xfs"
    "path"         = "/"
  }
  tags = {
    "billingtag" = "ukmon"
  }
}


resource "aws_cloudwatch_metric_alarm" "calcServerIdle" {
  alarm_name                = "CalcServer idle shutdown"
  comparison_operator       = "LessThanOrEqualToThreshold"
  evaluation_periods        = "6"
  metric_name               = "CPUUtilization"
  namespace                 = "AWS/EC2"
  period                    = "300"
  statistic                 = "Maximum"
  threshold                 = "0.5"
  alarm_description         = "CPUUtilization <= 0.5 for 6 datapoints within 30 minutes"
  insufficient_data_actions = []
  ok_actions                = []
  datapoints_to_alarm       = 6
  alarm_actions = [
    aws_sns_topic.ukmonalerts.arn,
    "arn:aws:swf:eu-west-2:317976261112:action/actions/AWS_EC2.InstanceId.Stop/1.0",
  ]
  dimensions = {
    "InstanceId" = aws_instance.CalcEngine4ARM.id
  }
  tags = {
    "billingtag" = "ukmon"
  }
}
