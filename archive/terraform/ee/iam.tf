##############################################################################
# role for EC2 servers 
resource "aws_iam_role" "calcserverrole" {
  name        = "CalcServerRole"
  description = "Allows EC2 CalcServer to connect to resources"
  path        = "/service-role/"
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
}
resource "aws_iam_instance_profile" "calcserverrole" {
  name = "CalcServerRole"
  role = aws_iam_role.calcserverrole.name
}

resource "aws_iam_role_policy_attachment" "calcserverpolatt" {
  role       = aws_iam_role.calcserverrole.name
  policy_arn = aws_iam_policy.calcserverpol.arn
}

data "template_file" "calcserpoltempl" {
  template = file("files/policies/ukmon-calcserverpolicy.json")

  vars = {
    ecsarn = aws_iam_role.ecstaskrole.arn
  }
}

resource "aws_iam_policy" "calcserverpol" {
  name   = "CalcServerPolicy"
  policy = data.template_file.calcserpoltempl.rendered
  tags = {
    "billingtag" = "ukmon"
  }
}
##############################################################################
# role used by Lambda functions
resource "aws_iam_role" "S3FullAccess" {
  name = "S3FullAccess"
  #description = "Allows EC2 instances to connect to S3"
  path = "/service-role/"
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
        {
          # not sure this one is used, double check 
          Action = "sts:AssumeRole"
          Effect = "Allow"
          Principal = {
            Service = "lambda.amazonaws.com"
            "AWS" : "arn:aws:iam::317976261112:root"
          }
        },
        {
          # give access to lambda functions in MJMM account
          Action = "sts:AssumeRole"
          Effect = "Allow"
          Principal = {
            AWS     = "arn:aws:iam::317976261112:role/lambda-s3-full-access-role"
            Service = "lambda.amazonaws.com"
          }
        },
        {
          # give access to S3FullAccess role used by EC2 in MJMM account
          Action = "sts:AssumeRole"
          Effect = "Allow"
          Principal = {
            AWS = "arn:aws:iam::317976261112:role/S3FullAccess"
          }
        },
        {
          # give access to ecsTaskRole role used by ECS in MJMM account
          Action = "sts:AssumeRole"
          Effect = "Allow"
          Principal = {
            AWS = "arn:aws:iam::317976261112:role/ecsTaskExecutionRole"
          }
        },
        {
          # give access to ecsTaskRole role used by ECS in EE account
          Action = "sts:AssumeRole"
          Effect = "Allow"
          Principal = {
            AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/ecsTaskExecutionRole"
          }
        },
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

resource "aws_iam_role_policy_attachment" "aws-managed-policy-attachment3" {
  role       = aws_iam_role.S3FullAccess.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}

resource "aws_iam_role_policy_attachment" "aws-managed-policy-attachment4" {
  role       = aws_iam_role.S3FullAccess.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

resource "aws_iam_role_policy_attachment" "aws-mps3" {
  role       = aws_iam_role.S3FullAccess.name
  policy_arn = "arn:aws:iam::822069317839:policy/service-role/AWSLambdaLambdaFunctionDestinationExecutionRole-5124b144-96bf-4873-b7fb-bf2724a4ec6b"
}

resource "aws_iam_role_policy_attachment" "aws-mps4" {
  role       = aws_iam_role.S3FullAccess.name
  policy_arn = "arn:aws:iam::822069317839:policy/ddbPermsForLambda"
}

resource "aws_iam_role_policy_attachment" "aws-mps5" {
  role       = aws_iam_role.S3FullAccess.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonAthenaFullAccess"
}

##############################################################################
##############################################################################
resource "aws_iam_user" "ukmonarchive" {
  name = "ukmonarchive"
}

resource "aws_iam_policy" "userpol1" {
  name = "CEforUkmonarchive"
  policy = jsonencode(
    {
      Statement = [
        {
          Action = [
            "ce:GetCostAndUsage",
            "ce:GetDimensionValues"
          ]
          Effect   = "Allow"
          Resource = "*"
          Sid      = "VisualEditor0"
        },
      ]
      Version = "2012-10-17"
    }
  )
  tags = {
    "billingtag" = "ukmon"
  }
}

resource "aws_iam_user_policy_attachment" "ump1" {
  user       = aws_iam_user.ukmonarchive.name
  policy_arn = aws_iam_policy.userpol1.arn
}

##############################################################################
# readonly user for GUI toolset
resource "aws_iam_user" "ukmonreadonly" {
  name = "ukmonreadonly"
  tags = {
    "billingtag" = "ukmon"
  }
}

resource "aws_iam_user_policy" "ukmon_ro_pol" {
  name = "ukmon_ro"
  user = aws_iam_user.ukmonreadonly.name

  policy = jsonencode(
    {
      Version = "2012-10-17"
      Statement = [
        {
          Action = [
            "s3:ListBucket",
            "s3:GetObject",
          ]
          Effect = "Allow"
          Resource = [
            "${aws_s3_bucket.ukmonshared.arn}/*",
            "${aws_s3_bucket.ukmonshared.arn}",
          ]
        }
      ]
    }
  )
}

resource "aws_iam_access_key" "ukmro_key" {
  user = aws_iam_user.ukmonreadonly.name
}

##############################################################################
# policy applied to all ukmon members to enable uploads 
resource "aws_iam_policy" "ukmonsharedpol" {
  name        = "UKMON-shared"
  description = "policy to allow single bucket access"
  policy      = file("files/policies/ukmon-shared.json")
  tags = {
    "billingtag" = "ukmon"
  }
}
##############################################################################
# policy applied to all ukmon members to enable livefeed
resource "aws_iam_policy" "ukmonlivepol" {
  name        = "UkmonLive"
  description = "Access to the ukmon-live s3 bucket for upload purposes"
  policy      = file("files/policies/ukmonlive.json")
  tags = {
    "billingtag" = "ukmon"
  }
}

##############################################################################
# role and permissions used by SAM functions 
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
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "aws_managed_policy_l4" {
  role       = aws_iam_role.lambda-s3-full-access-role.name
  policy_arn = "arn:aws:iam::822069317839:policy/ddbPermsForLambda"
}

resource "aws_iam_role_policy" "lambda_inline_policy_1" {
  name   = "policygen-lambda-s3-full-access-role"
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

# role and permissions used cloudwatch to shutdown servers
resource "aws_iam_service_linked_role" "cweventslrole" {
  description      = "Allows Cloudwatch Events to manage servers"
  aws_service_name = "events.amazonaws.com"
}

resource "aws_iam_role_policy_attachment" "cweventspolicy" {
  role       = aws_iam_service_linked_role.cweventslrole.name
  policy_arn = "arn:aws:iam::aws:policy/aws-service-role/CloudWatchEventsServiceRolePolicy"
}

