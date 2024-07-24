bucket         = "terraform-state-${var.aws_account_id}"
dynamodb_table = "terraform-lock"
encrypt        = true
key            = "${var.project}/terraform.tfstate"
region         = "eu-west-2"
