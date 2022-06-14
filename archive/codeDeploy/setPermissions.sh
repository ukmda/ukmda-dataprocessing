#!/bin/bash
echo chowning parent folder
chown ec2-user:ec2-user /home/ec2-user/test
chmod  0754 /home/ec2-user/test
echo chowning child folders
chown -R ec2-user:ec2-user /home/ec2-user/test/*
find /home/ec2-user/test -name "*.py" -exec chmod 0644 {} \;
find /home/ec2-user/test -name "*.sh" -exec chmod 0754 {} \;
