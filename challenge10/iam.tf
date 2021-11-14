resource "aws_iam_user" "ctf-demo-user" {
  name = "ctf-demo-user"
  path = "/"

  tags = {
    Name = "ctf-demo-user"
  }
}