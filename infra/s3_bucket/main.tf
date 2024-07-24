resource "aws_s3_bucket" "project_bucket" {
  bucket = "${var.project}-bucket-${var.aws_account_id}"
}

data "aws_iam_policy_document" "project_bucket_policy" {
  statement {
    actions   = ["s3:GetObject"]
    resources = ["arn:aws:s3:::${aws_s3_bucket.project_bucket.bucket}/*"]
    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
  }
}

resource "aws_s3_bucket_policy" "project_bucket_policy" {
  bucket = aws_s3_bucket.project_bucket.bucket

  policy = data.aws_iam_policy_document.project_bucket_policy.json
}