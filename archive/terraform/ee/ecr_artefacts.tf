##############################################################################
# Copyright (c) 2018- Mark McIntyre
##############################################################################

# encryption/decryption key in the AWS KMS keystore
resource "aws_kms_key" "container_key" {
  description = "My KMS Key"
  tags = {
    "billingtag" = "ukmon"
  }
}

# create an ECR repository for the extrafiles image
resource "aws_ecr_repository" "extrafilesrepo" {
  name                 = "ukmon/extrafiles"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
  encryption_configuration {
    encryption_type = "KMS"
    kms_key         = aws_kms_key.container_key.arn
  }
  tags = {
    "billingtag" = "ukmon"
  }
}

# create an ECR repository for FTPtoUKMON
resource "aws_ecr_repository" "ftptoukmonrepo" {
  name                 = "ukmon/ftptoukmon"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
  encryption_configuration {
    encryption_type = "KMS"
    kms_key         = aws_kms_key.container_key.arn
  }
  tags = {
    "billingtag" = "ukmon"
  }
}
resource "aws_ecr_lifecycle_policy" "extrafilespolicy" {
  repository = aws_ecr_repository.extrafilesrepo.name
  policy     = <<EOF
{
    "rules": [
        {
            "rulePriority": 1,
                        "description": "Keep only latest two versions images",
            "selection": {
                "tagStatus": "any",
                "countType": "imageCountMoreThan",
                "countNumber": 2
            },
            "action": {
                "type": "expire"
            }
        }
    ]
}
EOF
}

resource "aws_ecr_lifecycle_policy" "ftpyoukmonpolicy" {
  repository = aws_ecr_repository.ftptoukmonrepo.name
  policy     = <<EOF
{
    "rules": [
        {
            "rulePriority": 1,
                        "description": "Keep only latest two versions images",
            "selection": {
                "tagStatus": "any",
                "countType": "imageCountMoreThan",
                "countNumber": 2
            },
            "action": {
                "type": "expire"
            }
        }
    ]
}
EOF
}
