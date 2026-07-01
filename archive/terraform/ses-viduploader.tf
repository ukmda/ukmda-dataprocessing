# SES rules to manage email 

resource "aws_ses_receipt_rule_set" "ukmon_rs" {
  rule_set_name = "ukmon-rule-set"
}

resource "aws_ses_active_receipt_rule_set" "ukmon_rs" {
  rule_set_name = aws_ses_receipt_rule_set.ukmon_rs.rule_set_name
}

#data "aws_lambda_function" "vidhandler_lambda" {
#  function_name = "video_handler"
#}

resource "aws_ses_receipt_rule" "vidhandler" {
  name          = "Save-video"
  rule_set_name = aws_ses_receipt_rule_set.ukmon_rs.rule_set_name
  recipients    = ["vrec2026@ukmeteors.co.uk"]
  enabled       = true
  scan_enabled  = true

  s3_action {
    bucket_name       = aws_s3_bucket.ukmdashared.id
    object_key_prefix = "fireballs/videouploads/raw/"
    position          = 1
    iam_role_arn = aws_iam_role.vidUploadRole.arn
  }
#  lambda_action {
#    function_arn    = data.aws_lambda_function.vidhandler_lambda.arn
#    invocation_type = "Event"
#    position        = 2
#  }
}

