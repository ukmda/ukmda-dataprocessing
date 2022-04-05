# ssh keys
resource "aws_key_pair" "marks_key2" {
  key_name = "marks_key2"
  public_key = file("./ssh-keys/markskey.pub")
}