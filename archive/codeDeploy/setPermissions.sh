#!/bin/bash
echo chowning parent folder
chown ec2-user:ec2-user /home/ec2-user/test
chmod  0754 /home/ec2-user/test
echo chowning child folders
chown -R ec2-user:ec2-user /home/ec2-user/test/*
chmod -R 0644 /home/ec2-user/test/*.py
chmod -R 0754 /home/ec2-user/test/*.sh
