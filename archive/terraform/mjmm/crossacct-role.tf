# Copyright (C) 2018-2023 Mark McIntyre

data "aws_caller_identity" "eeacct" {provider = aws.eeacct }

# RESTRICT THESE PERMISSIONS!!
data "aws_iam_policy" "terraformpol" {
  name     = "AdministratorAccess"
}

data "aws_iam_policy_document" "terraformpoldoc" {
  statement {
    actions = [
      "sts:AssumeRole",
      "sts:TagSession",
      "sts:SetSourceIdentity"
    ]
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.eeacct.account_id}:root"]
    }
  }
  statement {
    actions = [
      "sts:AssumeRole",
      "sts:TagSession",
      "sts:SetSourceIdentity"
    ]
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${var.mda_account_id}:root"]
    }
  }
}

resource "aws_iam_role" "terraformrole" {
  name                = "TerraformRole"
  assume_role_policy  = data.aws_iam_policy_document.terraformpoldoc.json
  managed_policy_arns = [data.aws_iam_policy.terraformpol.arn]
  tags                = {
    billingtag = "ukmon"
  }
}
