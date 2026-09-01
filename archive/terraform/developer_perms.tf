# copyright (c) Mark McIntyre, 2024-

# Terraform to create the developer role and permissions

resource "aws_iam_group" "dev_group" {
    name = "developers"
}

resource "aws_iam_group_policy" "developer_policy_s3" {
  name  = "developer_policy_s3"
  group = aws_iam_group.dev_group.name
  policy      = data.template_file.developer_pol_templ.rendered
}

data "template_file" "developer_pol_templ" {
  template = file("files/policies/developer.json")
  vars = {
    sharedarn = aws_s3_bucket.ukmdashared.arn
    websitearn = aws_s3_bucket.archsite.arn
    livearn = aws_s3_bucket.ukmdalive.arn
  }
}

resource "aws_iam_group_policy_attachment" "devpol_cloud9_att" {
  group      = aws_iam_group.dev_group.name
  policy_arn = "arn:aws:iam::aws:policy/AWSCloud9User"
}


resource "aws_iam_group_policy_attachment" "devpol_other_att" {
  group      = aws_iam_group.dev_group.name
  policy_arn = aws_iam_policy.developerpolicy_other.arn
}

resource "aws_iam_policy" "developerpolicy_other" {
  name   = "developer_policy_ex_s3"
  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "DeveloperPolicies",
            "Effect": "Allow",
            "Action": [
      			  "logs:*",
      			  "ec2:*",
              "ec2messages:*",
              "ecs:*",
              "ecr:*",
              "dynamodb:*",
              "ses:*",
              "lambda:*",
              "ssm:*",
              "ssmmessages:*",
              "iam:Get*"
            ],
            "Resource": "*"
        }
    ]
}
EOF
}
