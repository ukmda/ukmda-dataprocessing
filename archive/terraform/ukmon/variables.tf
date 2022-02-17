variable "profile" {
    description = "AWS creds to use"
    default = "ukmonshared"
}
variable "region" {
        default = "eu-west-2"
}

variable "access_key" {
    description = "Access Key"
    default = ""
}

variable "secret_key" {
    description = "Secret Key"
    default = ""
}

variable "bucket_name" {
    default = "ukmeteornetworkarchive"
}
