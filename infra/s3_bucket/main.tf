resource "aws_s3_bucket" "project_bucket" {
  bucket = "${var.project}-bucket-${var.aws_account_id}"
}