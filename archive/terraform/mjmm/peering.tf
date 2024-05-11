# Copyright (C) 2018-2023 Mark McIntyre
#
# Terraform for peering to the ukmda account
#

resource "aws_vpc_peering_connection_accepter" "mdatommpeering" {
  vpc_peering_connection_id = "pcx-0beef413172ec795e"
  tags = {
    "Name"       = "ukmda-to-mm-peering"
    "billingtag" = "ukmda"
  }
}
