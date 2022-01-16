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
}

resource "aws_iam_role_policy_attachment" "aws-managed-policy-attachment1" {
  role       = aws_iam_role.S3FullAccess.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_role_policy_attachment" "aws-managed-policy-attachment2" {
  role       = aws_iam_role.S3FullAccess.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# User, Policy and Roles used to mount s3 buckets. 
resource "aws_iam_user" "s3user" {
  name = "s3user"
}

resource "aws_iam_policy" "MMS3BucketAccessRW" {
  name        = "MMS3BucketAccessRW"
  policy      = data.aws_iam_policy_document.MMS3BucketAccessRW-policy-doc.json
  description = "Access to MM S3 Buckets"
}

data "aws_iam_policy_document" "MMS3BucketAccessRW-policy-doc" {
  statement {
    actions = ["s3:ListBucket"]
    effect  = "Allow"
    resources = [
      "arn:aws:s3:::mlm-website-backups",
      "arn:aws:s3:::mjmm-website-backups",
      "arn:aws:s3:::mjmm-meteor-uploads",
      "arn:aws:s3:::mjmm-data",
    ]
    sid = "VisualEditor0"
  }
  statement {
    actions = [
      "s3:PutObject",
      "s3:GetObject",
      "s3:DeleteObject",
    ]
    effect = "Allow"
    resources = [
      "arn:aws:s3:::mjmm-data/*",
      "arn:aws:s3:::mjmm-meteor-uploads/*",
      "arn:aws:s3:::mlm-website-backups/*",
      "arn:aws:s3:::mjmm-website-backups/*",
    ]
    sid = "VisualEditor1"
  }
}

resource "aws_iam_user_policy_attachment" "s3user-pol-attachment" {
  user       = aws_iam_user.s3user.name
  policy_arn = "arn:aws:iam::317976261112:policy/MMS3BucketAccessRW"
}

#inline policy used by s3user
resource "aws_iam_user_policy" "Ukmon-shared-access" {
  name = "Ukmon-shared-access"
  user = aws_iam_user.s3user.name
  policy = jsonencode(
    {
      Statement = [
        {
          Action = [
            "s3:GetObject",
            "s3:PutObject",
            "s3:PutObjectAcl",
          ]
          Effect   = "Allow"
          Resource = "arn:aws:s3:::ukmon-shared/*"
        },
      ]
      Version = "2012-10-17"
    }
  )
}

# User, Policy and Roles used by ukmon-backup process. 
resource "aws_iam_user" "ukmon-backup" {
  name = "ukmon-backup"
}

resource "aws_iam_policy" "pol-ukmon-backup" {
  name        = "pol-ukmon-backup"
  policy      = data.aws_iam_policy_document.ukmon-backup-policy-document.json
  description = "allows a user to backup the UKMON shared data"
}

data "aws_iam_policy_document" "ukmon-backup-policy-document" {
  statement {
    actions = [
      "s3:ListBucket",
      "s3:GetObject",
    ]
    effect = "Allow"
    resources = [
      "arn:aws:s3:::ukmon-shared",
      "arn:aws:s3:::ukmon-shared/*",
    ]
  }
  statement {
    actions = [
      "s3:ListBucket",
      "s3:PutObject",
      "s3:PutObjectAcl",
    ]
    effect = "Allow"
    resources = [
      "arn:aws:s3:::ukmon-shared-backup",
      "arn:aws:s3:::ukmon-shared-backup/*",
    ]
  }
  version = "2012-10-17"
}

resource "aws_iam_user_policy_attachment" "ukmon-shared-pol-attachment" {
  user       = aws_iam_user.ukmon-backup.name
  policy_arn = "arn:aws:iam::317976261112:policy/pol-ukmon-backup"
}
