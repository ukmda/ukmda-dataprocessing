# Copyright (C) 2018-2023 Mark McIntyre

variable "profile" { default = "default" }
variable "region" { default = "eu-west-2" }

variable "remote_profile" { default = "ukmonshared"}
variable "remote_account_id" { default = "822069317839" }
variable "remote_region" {default = "eu-west-2"}
variable "mda_account_id" { default = "183798037734" }

variable "archbucket" {default = "ukmeteornetworkarchive"}
variable "sharedbucket" {default = "ukmon-shared"}
variable "livebucket" {default = "ukmon-live"}
