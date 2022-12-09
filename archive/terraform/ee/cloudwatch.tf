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
    "ImageId"      = aws_instance.calc_server.ami
    "InstanceId"   = aws_instance.calc_server.id
    "InstanceType" = aws_instance.calc_server.instance_type
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
  datapoints_to_alarm       = 4
  alarm_actions = [
    aws_sns_topic.ukmonalerts.arn,
    "arn:aws:automate:${var.region}:ec2:stop",
  ]
  dimensions = {
    "InstanceId" = aws_instance.calc_server.id
  }
  tags = {
    "billingtag" = "ukmon"
  }
}
