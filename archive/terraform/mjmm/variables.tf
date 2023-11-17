# Copyright (C) 2018-2023 Mark McIntyre

variable "profile" { default = "default" }
variable "region" { default = "eu-west-2" }

variable "remote_profile" { default = "ukmonshared"}
variable "remote_account_id" { default = "822069317839" }
variable "remote_region" {default = "eu-west-2"}
variable "mda_account_id" { default = "183798037734" }

variable "webbucket" {default = "ukmda-website"}
variable "sharedbucket" {default = "ukmda-shared"}
variable "livebucket" {default = "ukmda-live"}

variable "dev_sharedbucket" { default = "mjmm-ukmon-shared" }
variable "dev_webbucket" { default = "mjmm-ukmonarchive.co.uk" }
variable "dev_livebucket" { default = "mjmm-ukmon-live" }
variable "dev_oldsharedbucket" { default = "mjmm-old-ukmshared"}
variable "dev_oldwebbucket" { default = "mjmm-old-ukmweb"}
