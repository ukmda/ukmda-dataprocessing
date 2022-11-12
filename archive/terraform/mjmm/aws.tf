provider "aws" {
  profile = var.profile
  region  = var.region
}

provider "aws" {
  alias  = "eeacct"
  region = var.remote_region
  profile = "ukmonshared"
}

