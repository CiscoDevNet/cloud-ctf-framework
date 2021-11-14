resource "aws_iam_account_password_policy" "strict" {
  minimum_password_length        = 6
  password_reuse_prevention      = 5
}