##############################################################################
# role for EC2 servers 
# Copyright (C) 2018-2023 Mark McIntyre

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
  template = file("files/policies/ukmda-calcserverpolicy.json")

  vars = {
    ecsarn = aws_iam_role.ecstaskrole.arn
  }
}

resource "aws_iam_policy" "calcserverpol" {
  name   = "CalcServerPolicy"
  policy = data.template_file.calcserpoltempl.rendered
  tags = {
    "billingtag" = "ukmda"
  }
}
##############################################################################
# OIDC connector for github actions, allows testing to be executed in a container
resource "aws_iam_openid_connect_provider" "oidc_github" {
  url = "https://token.actions.githubusercontent.com"
  client_id_list = [ "sts.amazonaws.com" ]
  thumbprint_list = [ "1b511abead59c6ce207077c0bf0e0043b1382612" ]
  tags            = {
    "billingtag" = "ukmda"
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
            "AWS" : "arn:aws:iam::${var.remote_account_id}:root"
          }
        },
        {
          # give access to lambda functions in MJMM account
          Action = "sts:AssumeRole"
          Effect = "Allow"
          Principal = {
            AWS     = "arn:aws:iam::${var.remote_account_id}:role/lambda-s3-full-access-role"
            Service = "lambda.amazonaws.com"
          }
        },
        {
          # give access to S3FullAccess role used by EC2 in MJMM account
          Action = "sts:AssumeRole"
          Effect = "Allow"
          Principal = {
            AWS = "arn:aws:iam::${var.remote_account_id}:role/S3FullAccess"
          }
        },
        {
          # give access to ecsTaskRole role used by ECS in MJMM account
          Action = "sts:AssumeRole"
          Effect = "Allow"
          Principal = {
            AWS = "arn:aws:iam::${var.remote_account_id}:role/ecsTaskExecutionRole"
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
        }
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
  policy_arn = aws_iam_policy.lambdadestexecution.arn
}

resource "aws_iam_role_policy_attachment" "aws-mps4" {
  role       = aws_iam_role.S3FullAccess.name
  policy_arn = aws_iam_policy.ddbforlambda.arn
}

resource "aws_iam_role_policy_attachment" "aws-mps5" {
  role       = aws_iam_role.S3FullAccess.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonAthenaFullAccess"
}

###############################################################
# Role for testing from a container in GitHub
resource "aws_iam_role" "testing_role" {
  name = "testingRole"
  description = "Allows test containers to connect to AWS"
  assume_role_policy = jsonencode(
    {
      Version   = "2008-10-17"
      Statement = [
        {
          "Action": "sts:AssumeRole",
          "Principal": {
            "Service": "lambda.amazonaws.com"
          },
          "Effect": "Allow",
          "Sid": ""
        },
        {
          Action = "sts:AssumeRoleWithWebIdentity"
          Effect = "Allow"
          Principal =  {
            Federated =  aws_iam_openid_connect_provider.oidc_github.arn
          }          
          Condition =  {
            StringEquals =  {
              "token.actions.githubusercontent.com:sub": "repo:ukmda/ukmda-dataprocessing:ref:refs/heads/dev",
              "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
              }
          }
        },
        {
          Action = "sts:AssumeRoleWithWebIdentity"
          Effect = "Allow"
          Principal =  {
            Federated =  aws_iam_openid_connect_provider.oidc_github.arn
          }          
          Condition =  {
            StringEquals =  {
              "token.actions.githubusercontent.com:sub": "repo:ukmda/ukmda-dataprocessing:ref:refs/heads/master",
              "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
              }
          }
        },
        {
          Action = "sts:AssumeRoleWithWebIdentity"
          Effect = "Allow"
          Principal =  {
            Federated =  aws_iam_openid_connect_provider.oidc_github.arn
          }          
          Condition =  {
            StringEquals =  {
              "token.actions.githubusercontent.com:sub": "repo:ukmda/ukmda-dataprocessing:ref:refs/heads/markmac99",
              "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
              }
          }
        },
        {
          Action = "sts:AssumeRoleWithWebIdentity"
          Effect = "Allow"
          Principal =  {
            Federated =  aws_iam_openid_connect_provider.oidc_github.arn
          }          
          Condition =  {
            StringEquals =  {
              "token.actions.githubusercontent.com:sub": "repo:ukmda/ukmda-dataprocessing:pull_request",
              "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
              }
          }
        }
      ]
    }
  )
}

resource "aws_iam_role_policy" "monitorlive_policy_test" {
  name   = "monitorLivePolicy_test"
  role   = aws_iam_role.testing_role.id
  policy = data.template_file.livemonitorlambdatempl.rendered
}  

resource "aws_iam_role_policy_attachment" "test_s3access" {
  role       = aws_iam_role.testing_role.id
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

##############################################################################
resource "aws_iam_group" "admin_group" {
  name = "Administrators"
}

resource "aws_iam_group_policy_attachment" "admin_perms_att" {
  group      = aws_iam_group.admin_group.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

resource "aws_iam_group_policy_attachment" "fbcadm_perms_att" {
  group      = aws_iam_group.admin_group.name
  policy_arn = aws_iam_policy.fbc_assumerole_pol.arn
}

##############################################################################

resource "aws_iam_group" "camera_group" {
  name = "cameras"
}

# policy applied to all ukmda members to enable uploads 
data "template_file" "ukmshared_pol_templ" {
  template = file("files/policies/ukmda-shared.json")
  vars = {
    sharedarn = aws_s3_bucket.ukmdashared.arn
    websitearn = aws_s3_bucket.archsite.arn
  }
}

resource "aws_iam_policy" "ukmdasharedpol" {
  name        = "UKMDA-shared"
  description = "policy to allow single bucket access"
  policy      = data.template_file.ukmshared_pol_templ.rendered
  tags = {
    "billingtag" = "ukmda"
  }
}
##############################################################################
# policy applied to all ukmda members to enable livefeed
data "template_file" "ukmlive_pol_templ" {
  template = file("files/policies/ukmdalive.json")
  vars = {
    livearn = aws_s3_bucket.ukmdalive.arn
  }
}

resource "aws_iam_policy" "ukmdalivepol" {
  name        = "UkmonLive"
  description = "Access to the ukmda-live s3 bucket for upload purposes"
  policy      = data.template_file.ukmlive_pol_templ.rendered
  tags = {
    "billingtag" = "ukmda"
  }
}

resource "aws_iam_group_policy_attachment" "camgrp_shrpol_att1" {
  group      = aws_iam_group.camera_group.name
  policy_arn = aws_iam_policy.ukmdasharedpol.arn
}

resource "aws_iam_group_policy_attachment" "camgrp_livepol_att" {
  group      = aws_iam_group.camera_group.name
  policy_arn = aws_iam_policy.ukmdalivepol.arn
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
  policy_arn = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:policy/ddbPermsForLambda"
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

/*
# role and permissions used cloudwatch to shutdown servers
resource "aws_iam_service_linked_role" "cweventslrole" {
  description      = "Allows Cloudwatch Events to manage servers"
  aws_service_name = "events.amazonaws.com"
}

resource "aws_iam_role_policy_attachment" "cweventspolicy" {
  role       = aws_iam_service_linked_role.cweventslrole.name
  policy_arn = "arn:aws:iam::aws:policy/aws-service-role/CloudWatchEventsServiceRolePolicy"
}
*/
##############################################################
#  Dynamodb live table access 
##############################################################
data "template_file" "ddblive_pol_templ" {
  template = file("files/policies/ddb_livetables.json")
  vars = {
    brighttblarn = aws_dynamodb_table.live_bright_table.arn
    livetblarn = aws_dynamodb_table.live_table.arn
  }
}

resource "aws_iam_policy" "livetablepol" {
  name        = "LiveTableReadOnlyDynamoDb"
  #description = "policy to allow readonly access to live and LiveBrightness tables"
  policy      = data.template_file.ddblive_pol_templ.rendered
  tags = {
    "billingtag" = "ukmda"
  }
}

resource "aws_iam_policy" "ddbforlambda" {
  name="ddbPermsForLambda"
policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogStream",
                "dynamodb:Scan",
                "dynamodb:Query",
                "logs:PutLogEvents"
            ],
            "Resource": [
                "arn:aws:dynamodb:*:${data.aws_caller_identity.current.account_id}:table/*/index/*",
                "arn:aws:logs:eu-west-1:${data.aws_caller_identity.current.account_id}:*"
            ]
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "dynamodb:BatchGetItem",
                "dynamodb:BatchWriteItem",
                "dynamodb:PutItem",
                "dynamodb:GetItem",
                "dynamodb:Scan",
                "dynamodb:Query",
                "dynamodb:UpdateItem"
            ],
            "Resource": "arn:aws:dynamodb:*:${data.aws_caller_identity.current.account_id}:table/*"
        },
        {
            "Sid": "VisualEditor2",
            "Effect": "Allow",
            "Action": "logs:CreateLogGroup",
            "Resource": "*"
        }
    ] 
}
EOF
}

resource "aws_iam_policy" "lambdadestexecution" {
  name="LambdaDestinationExecutionPerms"
policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "lambda:InvokeFunction",
            "Resource": "arn:aws:lambda:eu-west-1:${data.aws_caller_identity.current.account_id}:function:testWCPublish*"
        }
    ]
}
EOF
}

# role used by the Orbit Uploader API
resource "aws_iam_role" "orbUploadRole" {
  name        = "orbUploadRole"
  description = "Allows API Gateway to upload orbit files"
  assume_role_policy = jsonencode(
    {
      Statement = [
        {
          Action = "sts:AssumeRole"
          Effect = "Allow"
          Principal = {
            Service = "apigateway.amazonaws.com"
          }
        },
      ]
      Version = "2012-10-17"
    }
  )
}
# policy used by the Orbit Uploader API
resource "aws_iam_role_policy" "orbUploadPolicy" {
  name   = "orbUploadPolicy"
  role   = aws_iam_role.orbUploadRole.name
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
            "Resource": [
                "*"
            ]
        },
        {
            "Sid": "uploadFiles",
            "Effect": "Allow",
            "Action": [
                "s3:Put*"
            ],
            "Resource": [
                "*"
            ]
        }
    ]
}
EOF
}
