# Copyright (C) 2018-2023 Mark McIntyre

# Role and policies used by EC2 servers
resource "aws_iam_role" "S3FullAccess" {
  name        = "S3FullAccess"
  description = "Allows EC2 instances to connect to S3"
  assume_role_policy = jsonencode(
    {
      Statement = [
        {
          Action = "sts:AssumeRole"
          Effect = "Allow"
          Principal = {
            Service = "ec2.amazonaws.com"
          }
        },
      ]
      Version = "2012-10-17"
    }
  )
  tags = {
    "billingtag" = "ukmon"
  }
}

resource "aws_iam_instance_profile" "S3FullAccess" {
  name = "S3FullAccess"
  role = aws_iam_role.S3FullAccess.name
}

resource "aws_iam_role_policy_attachment" "aws-managed-policy-attachment1" {
  role       = aws_iam_role.S3FullAccess.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_role_policy_attachment" "aws-managed-policy-attachment2" {
  role       = aws_iam_role.S3FullAccess.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy_attachment" "xacctaccess" {
  role       = aws_iam_role.S3FullAccess.name
  policy_arn = aws_iam_policy.crossacctpolicy.arn
}

resource "aws_iam_role_policy_attachment" "polatt4s3fullaccess" {
  role       = aws_iam_role.S3FullAccess.name
  policy_arn = aws_iam_policy.pol4s3fullaccess.arn
}

resource "aws_iam_policy" "pol4s3fullaccess" {
  name = "PolForS3FullAccess"
  policy = jsonencode(
    {
      Statement = [
        {
          Action = [
            "logs:FilterLogEvents",
            "logs:GetLogEvents",
            "ec2:DescribeInstances",
            "ec2:StartInstances",
            "ec2:StopInstances",
            "ecs:DescribeClusters",
            "ecs:DescribeTasks",
            "ecs:RunTask",
            "s3:*",
          ]
          Effect = "Allow"
          Resource = [
            "*",
          ]
        },
        {
          Sid      = "PassRolePermission"
          Effect   = "Allow"
          Action   = [
            "iam:PassRole",
            "iam:GetRole",
            ]
          Resource = aws_iam_role.ecstaskrole.arn
        }
      ]
      Version = "2012-10-17"
    }
  )
  tags = {
    "billingtag" = "ukmon"
  }
}

resource "aws_iam_policy" "crossacctpolicy" {
  name = "CrossAcctPolForS3FullAccess"
  policy = jsonencode(
    {
      Statement = [
        {
          Action = [
            "sts:AssumeRole",
          ]
          Effect = "Allow"
          Resource = [
            "arn:aws:iam::822069317839:role/service-role/S3FullAccess",
            "arn:aws:iam::183798037734:role/service-role/S3FullAccess",
          ]
        },
        {
          Action = [
            "lambda:InvokeFunction",
          ]
          Effect = "Allow"
          Resource = [
            "arn:aws:lambda:eu-west-1:822069317839:function:dailyReport",
            "arn:aws:lambda:eu-west-1:183798037734:function:dailyReport",
          ]
        },
      ]
      Version = "2012-10-17"
    }
  )
  tags = {
    "billingtag" = "ukmon"
  }
}



# role and permissions used by Lambda 
resource "aws_iam_role" "lambda-s3-full-access-role" {
  name        = "lambda-s3-full-access-role"
  description = "Allows lambda acccess to S3 buckets"
  assume_role_policy = jsonencode(
    {
      Statement = [
        {
          Action = "sts:AssumeRole"
          Effect = "Allow"
          Principal = {
            Service = "lambda.amazonaws.com"
          }
        },
      ]
      Version = "2012-10-17"
    }
  )
}

resource "aws_iam_role_policy_attachment" "aws_managed_policy_l1" {
  role       = aws_iam_role.lambda-s3-full-access-role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}
resource "aws_iam_role_policy_attachment" "aws_managed_policy_l2" {
  role       = aws_iam_role.lambda-s3-full-access-role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}
resource "aws_iam_role_policy_attachment" "aws_managed_policy_l3" {
  role       = aws_iam_role.lambda-s3-full-access-role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSLambdaFullAccess"
}
resource "aws_iam_role_policy_attachment" "aws_managed_policy_l4" {
  role       = aws_iam_role.lambda-s3-full-access-role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

resource "aws_iam_role_policy" "lambda_inline_policy_1" {
  name   = "policygen-lambda-s3-full-access-role-201711082329"
  role   = aws_iam_role.lambda-s3-full-access-role.name
  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Stmt1510183751000",
            "Effect": "Allow",
            "Action": [
                "ses:SendEmail",
                "ses:SendRawEmail"
            ],
            "Resource": [
                "*"
            ]
        }
    ]
}
EOF
}

resource "aws_iam_role_policy" "stsAssumeLambda" {
  name = "assumeRolePol"
  role = aws_iam_role.lambda-s3-full-access-role.name
  policy = jsonencode(
    {
      Statement = {
        Action   = "sts:AssumeRole"
        Effect   = "Allow"
        Resource = "arn:aws:iam::822069317839:role/service-role/S3FullAccess"
      }
      Version = "2012-10-17"
    }
  )
}


# role and permissions used cloudwatch to shutdown servers
resource "aws_iam_service_linked_role" "cweventslrole" {
  description = "Allows Cloudwatch Events to manage servers"
  aws_service_name = "events.amazonaws.com"
}

resource "aws_iam_role_policy_attachment" "cweventspolicy" {
  role       = aws_iam_service_linked_role.cweventslrole.name
  policy_arn = "arn:aws:iam::aws:policy/aws-service-role/CloudWatchEventsServiceRolePolicy"
}




################################
# for testing with 

# User, Policy and Roles used by ukmon-backup process. 
# don't think this is used 
resource "aws_iam_user" "ukmon_tester" {
  name = "ukmon_tester"
  tags = {
    "billingtag" = "ukmon"
    "AKIAUUCG4WH4B3XOH3WZ" = "ukmon_tester"
  }
}

resource "aws_iam_policy" "pol_ukmon_tester" {
  name        = "pol_ukmon_tester"
  policy      = data.aws_iam_policy_document.ukmon_tester_pol_doc.json
  description = "policu for my test user"
}

data "aws_iam_policy_document" "ukmon_tester_pol_doc" {
  statement {
    actions = [
      "s3:*"
    ]
    effect = "Allow"
    resources = [
      "arn:aws:s3:::mjmm-ukmon-shared",
      "arn:aws:s3:::mjmm-ukmon-shared/*",
      "arn:aws:s3:::mjmm-ukmon-live",
      "arn:aws:s3:::mjmm-ukmon-live/*",
      "arn:aws:s3:::mjmm-ukmonarchive.co.uk",
      "arn:aws:s3:::mjmm-ukmonarchive.co.uk/*",
    ]
  }
  version = "2012-10-17"
}

resource "aws_iam_user_policy_attachment" "ukmon-tester-pol-attachment" {
  user       = aws_iam_user.ukmon_tester.name
  policy_arn = aws_iam_policy.pol_ukmon_tester.arn
}


