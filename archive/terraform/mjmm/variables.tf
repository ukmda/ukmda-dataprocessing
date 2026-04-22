# Copyright (C) 2018-2023 Mark McIntyre

variable "profile" { default = "default" }
variable "region" { default = "eu-west-2" }

variable "remote_profile" { default = "ukmonshared"}
variable "remote_region" {default = "eu-west-2"}
variable "mda_account_id" { default = "183798037734" }

variable "webbucket" {default = "ukmda-website"}
variable "sharedbucket" {default = "ukmda-shared"}
variable "livebucket" {default = "ukmda-live"}

variable "dev_webbucket" { default = "ukmda-website" }
variable "dev_sharedbucket" { default = "ukmda-shared" }
variable "dev_livebucket" { default = "ukmda-live" }

variable "vpc_id" { default = "vpc-a19015c8" }
