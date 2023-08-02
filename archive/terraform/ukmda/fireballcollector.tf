#
# stuff to support the fireball Collector tool
# Copyright (C) 2018-2023 Mark McIntyre
#
resource "aws_iam_role" "fbc_role" {
  name        = "fireballCollector"
  description = "Allows the fireball Collector to access resources"
  assume_role_policy = jsonencode(
    {
      Statement = [
        {
          Action = "sts:AssumeRole"
          Effect = "Allow"
          Principal = {
            AWS = data.aws_caller_identity.current.account_id
          }
        },
      ]
      Version = "2012-10-17"
    }
  )
}

resource "aws_iam_role_policy_attachment" "fbcoll_polatt" {
  role       = aws_iam_role.fbc_role.name
  policy_arn = aws_iam_policy.ukmda_fbcoll_pol.arn
}

resource "aws_iam_policy" "ukmda_fbcoll_pol" {
  name        = "fireballCollector_policy"
  description = "policy to allow S3 access for the fb collector tool"
  policy      = data.template_file.fbc_pol_templ.rendered
  tags = {
    "billingtag" = "ukmda"
  }
}

data "template_file" "fbc_pol_templ" {
  template = file("files/policies/fireballcollector-policy.json")
  vars = {
    livearn = aws_s3_bucket.ukmdalive.arn
    sharedarn = aws_s3_bucket.ukmdashared.arn
  }
}

resource "aws_iam_policy" "fbc_assumerole_pol" {
  name        = "fbc_assumerole"
  description = "policy to allow users to assume the FBC role"
  policy = jsonencode(
    {
      Version = "2012-10-17",
      Statement = [{
        Effect   = "Allow"
        Action   = "sts:AssumeRole"
        Resource = [aws_iam_role.fbc_role.arn,]
      }]
    }
  )
}

resource "aws_iam_user_policy_attachment" "fbatt1" {
  user = "MarkMcIntyreUKM"
  policy_arn = aws_iam_policy.fbc_assumerole_pol.arn
}

