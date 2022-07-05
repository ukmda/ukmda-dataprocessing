# stuff for CodeDeploy

# Role and policies used by EC2 servers
resource "aws_iam_role" "ec2_code_deploy_role" {
  name        = "codeDeployRoleEC2"
  description = "CodeDeploy role for EC2 instances"
  assume_role_policy = jsonencode(
    {
      Statement = [
        {
          Action = "sts:AssumeRole"
          Effect = "Allow"
          Principal = {
            Service = "codedeploy.amazonaws.com"
          }
        },
      ]
      Version = "2012-10-17"
    }
  )
  tags = {
    "billingtag" = "Management"
  }
}

resource "aws_iam_role_policy_attachment" "ec2_codedeploy_pol_att" {
  role       = aws_iam_role.ec2_code_deploy_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSCodeDeployRole"
}
