resource "aws_iam_user" "ukmonarchive" {
  name = "ukmonarchive"
}

resource "aws_iam_role" "S3FullAccess" {
  name = "S3FullAccess"
  #description = "Allows EC2 instances to connect to S3"
  path = "/service-role/"
  assume_role_policy = jsonencode(
    {
      Statement = [
        {
          # not sure this one is used, double check 
          Action = "sts:AssumeRole"
          Effect = "Allow"
          Principal = {
            Service = "lambda.amazonaws.com"
            "AWS": "arn:aws:iam::317976261112:root"
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
            AWS     = "arn:aws:iam::317976261112:role/S3FullAccess"
          }
        },
        {
          # give access to ecsTaskRole role used by ECS in MJMM account
          Action = "sts:AssumeRole"
          Effect = "Allow"
          Principal = {
            AWS     = "arn:aws:iam::317976261112:role/ecsTaskExecutionRole"
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

resource "aws_iam_role_policy_attachment" "aws-managed-policy-attachment1" {
  role       = aws_iam_role.S3FullAccess.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_role_policy_attachment" "aws-managed-policy-attachment3" {
  role       = aws_iam_role.S3FullAccess.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
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


resource "aws_iam_policy" "userpol1" {
  name = "CEforUkmonarchive"
  policy = jsonencode(
    {
      Statement = [
        {
          Action   = [
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
  user       = "ukmonarchive"
  policy_arn = aws_iam_policy.userpol1.arn
}

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

output "key" { value = aws_iam_access_key.ukmro_key.id}
output "secret" { 
  value = aws_iam_access_key.ukmro_key.secret
  sensitive = true
  }