# Security Baseline Terraform Module
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# CloudTrail for audit logging
resource "aws_cloudtrail" "security_trail" {
  name           = "security-audit-trail"
  s3_bucket_name = aws_s3_bucket.cloudtrail_bucket.bucket
  
  event_selector {
    read_write_type                 = "All"
    include_management_events       = true
    data_resource {
      type   = "AWS::S3::Object"
      values = ["arn:aws:s3:::*/*"]
    }
  }
  
  tags = {
    Environment = "security"
    Purpose     = "audit-logging"
  }
}

# S3 bucket for CloudTrail logs
resource "aws_s3_bucket" "cloudtrail_bucket" {
  bucket        = "security-cloudtrail-${random_id.bucket_suffix.hex}"
  force_destroy = true
}

resource "aws_s3_bucket_versioning" "cloudtrail_versioning" {
  bucket = aws_s3_bucket.cloudtrail_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_encryption" "cloudtrail_encryption" {
  bucket = aws_s3_bucket.cloudtrail_bucket.id
  
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

# Config for compliance monitoring
resource "aws_config_configuration_recorder" "security_recorder" {
  name     = "security-config-recorder"
  role_arn = aws_iam_role.config_role.arn
  
  recording_group {
    all_supported = true
  }
}

resource "aws_config_delivery_channel" "security_channel" {
  name           = "security-config-channel"
  s3_bucket_name = aws_s3_bucket.config_bucket.bucket
}

# Security Hub
resource "aws_securityhub_account" "main" {}

# GuardDuty
resource "aws_guardduty_detector" "main" {
  enable = true
  
  datasources {
    s3_logs {
      enable = true
    }
    kubernetes {
      audit_logs {
        enable = true
      }
    }
  }
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}
