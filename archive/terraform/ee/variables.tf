variable "profile" {
    description = "AWS creds to use"
    default = "ukmonshared"
}

variable "access_key" {
    description = "Access Key"
    default = ""
}

variable "secret_key" {
    description = "Secret Key"
    default = ""
}

variable "websitebucket" { default = "ukmeteornetworkarchive" }
variable "sharedbucket" { default = "ukmon-shared" }
variable "livebucket" { default = "ukmon-live" }
variable "region"{ default = "eu-west-2"}

#data used by the code in several places
data "aws_caller_identity" "current" {}

