# Copyright (C) 2018-2023 Mark McIntyre

variable "profile" {  default = "ukmda_admin" }
variable "mmprofile" { default = "default" }

variable "websitebucket" { default = "ukmda-website" }
variable "sharedbucket" { default = "ukmda-shared" }
variable "livebucket" { default = "ukmda-live" }
variable "adminbucket" { default = "ukmda-admin" }

variable "region" { default = "eu-west-2"}
variable "liveregion" { default = "eu-west-1"}

#data used by the code in several places
data "aws_caller_identity" "current" {}
data "aws_canonical_user_id" "current" {}

variable "remote_profile" { default = "default"}
variable "remote_account_id" { default = "317976261112" }
variable "remote_region" {default = "eu-west-2"}
#variable "eeaccountid" {default = "822069317839" }

variable "main_cidr" {default = "172.32.0.0/16" }
variable mgmt_cidr { default = "172.32.36.0/22" }
variable lambda_cidr { default = "172.32.32.0/22" }
variable ec2_cidr { default = "172.32.16.0/20" }
variable calcserverip { default = "172.32.16.136" }
variable ubuntu_calcserverip { default = "172.32.16.137" }


variable archalias { default = "archive.ukmeteors.co.uk"}
variable mainalias { default = "www.ukmeteors.co.uk"}
