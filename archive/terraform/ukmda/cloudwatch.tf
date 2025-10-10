#
# Cloudwatch alarms etc
#
# Copyright (C) 2018-2023 Mark McIntyre

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
    #aws_sns_topic.ukmda.arn,
    "arn:aws:automate:${var.region}:ec2:stop",
  ]
  dimensions = {
    "InstanceId" = aws_instance.calc_server.id
  }
  tags = {
    "billingtag" = "ukmda"
  }

   actions_enabled           = true
}

resource "aws_cloudwatch_log_group" "nightlyjob" {
  name = "/ukmonbatch/nightlyjob"
  retention_in_days = 60
  tags = {
    "billingtag" = "ukmda"
  }
}

resource "aws_cloudwatch_log_group" "devnightly" {
  name = "/ukmondev/nightlyjob"
  retention_in_days = 60
  tags = {
    "billingtag" = "ukmda"
  }
}
