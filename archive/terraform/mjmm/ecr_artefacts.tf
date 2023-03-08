# Copyright (C) 2018-2023 Mark McIntyre

# create ECR and ECS artefacts

# encryption/decryption key in the AWS KMS keystore
resource "aws_kms_key" "container_key" {
  description = "My KMS Key"
  tags = {
    "billingtag" = "ukmon"
  }
}


# create an ECR repository for the trajsolver images
resource "aws_ecr_repository" "trajsolverrepo" {
  name                 = "ukmon/trajsolver"
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
# create an ECR repository for the trajsolver test images
resource "aws_ecr_repository" "trajsolvertestrepo" {
  name                 = "ukmon/trajsolvertest"
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

# create an ECR repository for the extrafiles image
resource "aws_ecr_repository" "extrafilesrepo" {
  name                 = "mjmm-repo1"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
  tags = {
    "billingtag" = "ukmon"
  }
}

# create an ECR repository for the simpleui image
resource "aws_ecr_repository" "simpleuirepo" {
  name                 = "ukmon/simpleui"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
  tags = {
    "billingtag" = "mjmm"
  }
}


resource "aws_ecr_lifecycle_policy" "policy1" {
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

resource "aws_ecr_lifecycle_policy" "getfilespolicy" {
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

resource "aws_ecr_lifecycle_policy" "simpleuipol" {
  repository = aws_ecr_repository.simpleuirepo.name
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
*/