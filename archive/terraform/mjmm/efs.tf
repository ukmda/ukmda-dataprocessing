# EFS terraform bits
resource "aws_efs_file_system" "pylibsforLambda" {
  creation_token         = "quickCreated-890359a5-3e2e-4c5e-b473-a523a8d9d4be"
  availability_zone_name = "eu-west-2a"
  lifecycle_policy {
    transition_to_ia = "AFTER_30_DAYS"
  }
  lifecycle_policy {
    transition_to_primary_storage_class = "AFTER_1_ACCESS"
  }

  tags = {
    Name       = "pylibsforLambda",
    project    = "UKMonHelper",
    billingtag = "ukmon"
  }
}

resource "aws_efs_access_point" "pylibs" {
  file_system_id = aws_efs_file_system.pylibsforLambda.id
  posix_user {
    gid = 1001
    uid = 1001
  }
  root_directory {
    creation_info {
      owner_gid   = 1001
      owner_uid   = 1001
      permissions = 750
    }
    path = "/pylibs"
  }
  tags = {
    "Name"       = "pylibs"
    "billingtag" = "ukmon"
    "project"    = "UKMonHelper"
  }
}
