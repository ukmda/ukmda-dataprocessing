# Copyright (C) 2018-2023 Mark McIntyre

provider "aws" {
  profile = var.profile
  region  = var.region
}

provider "aws" {
  profile = var.profile
  region  = "eu-west-1"
  alias   = "eu-west-1-prov"
}
