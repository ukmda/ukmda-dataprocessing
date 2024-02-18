# terraform to manage user policies

resource "aws_iam_policy" "usermaintpolicy" {
  name   = "UserMaintPolicy"
  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowLogs",
            "Effect": "Allow",
            "Action": [
      			  "logs:CreateLogGroup",
      			  "logs:CreateLogStream"
            ],
            "Resource": "*"
        },
        {
            "Sid": "UserMgmtFiles",
            "Effect": "Allow",
            "Action": [
                "s3:Put*",
                "s3:Get*"
            ],
            "Resource": "${aws_s3_bucket.ukmdashared.arn}/consolidated/camera-details.csv"
        },
        {
            "Sid": "maintainCamtable",
            "Effect": "Allow",
            "Action": [
                "dynamodb:PutItem",
                "dynamodb:DeleteItem",
                "dynamodb:Query",
                "dynamodb:Scan"
            ],
            "Resource": "${aws_dynamodb_table.camera_table.arn}"
        },
        {
            "Sid": "checkCamStatus",
            "Effect": "Allow",
            "Action": [
                "dynamodb:Query"
            ],
            "Resource": "${aws_dynamodb_table.live_bright_table.arn}/*"
        },
        {
            "Sid": "IamPermissions",
            "Effect": "Allow",
            "Action": [
              "iam:GetUser",
              "iam:CreateUser",
              "iam:AttachUserPolicy",
              "iam:CreateAccessKey"
            ],
            "Resource": "*"
        }
    ]
}
EOF
}

resource "aws_iam_policy" "developerpolicy" {
  name   = "DeveloperPolicy"
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
