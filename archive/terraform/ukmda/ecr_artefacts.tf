# create ECR and ECS artefacts
# Copyright (C) 2018-2023 Mark McIntyre

# encryption/decryption key in the AWS KMS keystore
resource "aws_kms_key" "container_key" {
  description = "My KMS Key"
  tags = {
    "billingtag" = "ukmda"
  }
}

# create an ECR repository for the trajsolver images
resource "aws_ecr_repository" "trajsolverrepo" {
  name                 = "calcengine/trajsolver"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
  encryption_configuration {
    encryption_type = "KMS"
    kms_key         = aws_kms_key.container_key.arn
  }
  tags = {
    "billingtag" = "ukmda"
  }
}
# create an ECR repository for the trajsolver test images
resource "aws_ecr_repository" "trajsolvertestrepo" {
  name                 = "calcengine/trajsolvertest"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
  encryption_configuration {
    encryption_type = "KMS"
    kms_key         = aws_kms_key.container_key.arn
  }
  tags = {
    "billingtag" = "ukmda"
  }
}

# create an ECR repository for the extrafiles image
resource "aws_ecr_repository" "extrafilesrepo" {
  name                 = "lambdas/getextrafiles"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
  encryption_configuration {
    encryption_type = "KMS"
    kms_key         = aws_kms_key.container_key.arn
  }
  tags = {
    "billingtag" = "ukmda"
  }
}

# create an ECR repository for FTPtoUKMON
resource "aws_ecr_repository" "ftptoukmdarepo" {
  name                 = "lambdas/ftptoukmon"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
  encryption_configuration {
    encryption_type = "KMS"
    kms_key         = aws_kms_key.container_key.arn
  }
  tags = {
    "billingtag" = "ukmda"
  }
}

# create an ECR repository for matthpickleapi
resource "aws_ecr_repository" "matchpickleapirepo" {
  name                 = "apis/matchpickleapi"
  image_tag_mutability = "MUTABLE"
  provider = aws.eu-west-1-prov

  image_scanning_configuration {
    scan_on_push = true
  }
#  encryption_configuration {
#    encryption_type = "KMS"
#    kms_key         = aws_kms_key.container_key.arn
#  }
  tags = {
    "billingtag" = "ukmda"
  }
}

resource "aws_ecr_lifecycle_policy" "trajsolverpolicy" {
  repository = aws_ecr_repository.trajsolverrepo.name
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
resource "aws_ecr_lifecycle_policy" "trajssolvertestpolicy" {
  repository = aws_ecr_repository.trajsolvertestrepo.name
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

resource "aws_ecr_lifecycle_policy" "ftpoukmdapolicy" {
  repository = aws_ecr_repository.ftptoukmdarepo.name
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

resource "aws_ecr_lifecycle_policy" "matchpicklepolicy" {
  repository = aws_ecr_repository.matchpickleapirepo.name
  provider = aws.eu-west-1-prov
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

/*
output "trajsolverid" {
  value = aws_ecr_repository.trajsolverrepo.repository_url
}
output "trajsolvertestid" {
  value = aws_ecr_repository.trajsolvertestrepo.repository_url
}
output "extrafilesid" {
  value = aws_ecr_repository.extrafilesrepo.repository_url
}
output "sparkrepoid" {
  value = aws_ecr_repository.sparkrepo.repository_url
}
*/