resource "aws_iam_account_password_policy" "strict" {
  minimum_password_length        = 14
  password_reuse_prevention      = 0
}