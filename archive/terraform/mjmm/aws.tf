# Copyright (C) 2018-2023 Mark McIntyre

variable "profile" { default = "default" }
variable "region" { default = "eu-west-2" }

provider "aws" {
  profile = var.profile
  region  = var.region
}

provider "aws" {
  profile = var.profile
  region  = "eu-west-1"
  alias   = "eu-west-1-prov"
}
