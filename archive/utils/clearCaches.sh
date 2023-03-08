#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre

sudo sync
sudo echo "1" > /tmp/1.txt
sudo cp /tmp/1.txt /proc/sys/vm/drop_caches


