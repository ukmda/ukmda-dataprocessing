variable "profile" {  default = "ukmonshared" }

variable "websitebucket" { default = "ukmeteornetworkarchive" }
variable "sharedbucket" { default = "ukmon-shared" }
variable "livebucket" { default = "ukmon-live" }
variable "region"{ default = "eu-west-2"}

#data used by the code in several places
data "aws_caller_identity" "current" {}
data "aws_canonical_user_id" "current" {}

variable "remote_profile" { default = "default"}
variable "remote_account_id" { default = "317976261112" }
variable "remote_region" {default = "eu-west-2"}
