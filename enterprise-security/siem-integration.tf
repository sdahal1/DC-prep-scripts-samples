# SIEM Integration with AWS Services
resource "aws_kinesis_stream" "security_logs" {
  name             = "security-log-stream"
  shard_count      = 2
  retention_period = 168
  
  encryption_type = "KMS"
  kms_key_id      = aws_kms_key.security_key.arn
  
  tags = {
    Environment = "security"
    Purpose     = "siem-integration"
  }
}

# Kinesis Firehose for log delivery
resource "aws_kinesis_firehose_delivery_stream" "security_firehose" {
  name        = "security-log-delivery"
  destination = "opensearch"
  
  opensearch_configuration {
    domain_arn = aws_opensearch_domain.security_logs.arn
    role_arn   = aws_iam_role.firehose_role.arn
    index_name = "security-logs"
    
    processing_configuration {
      enabled = true
      
      processors {
        type = "Lambda"
        
        parameters {
          parameter_name  = "LambdaArn"
          parameter_value = aws_lambda_function.log_processor.arn
        }
      }
    }
  }
}

# OpenSearch domain for log analysis
resource "aws_opensearch_domain" "security_logs" {
  domain_name    = "security-logs"
  engine_version = "OpenSearch_2.3"
  
  cluster_config {
    instance_type  = "t3.small.search"
    instance_count = 2
  }
  
  ebs_options {
    ebs_enabled = true
    volume_type = "gp3"
    volume_size = 20
  }
  
  encrypt_at_rest {
    enabled = true
  }
  
  node_to_node_encryption {
    enabled = true
  }
  
  domain_endpoint_options {
    enforce_https = true
  }
}

# Lambda function for log processing
resource "aws_lambda_function" "log_processor" {
  filename         = "log_processor.zip"
  function_name    = "security-log-processor"
  role            = aws_iam_role.lambda_role.arn
  handler         = "index.handler"
  runtime         = "python3.9"
  
  environment {
    variables = {
      OPENSEARCH_ENDPOINT = aws_opensearch_domain.security_logs.endpoint
    }
  }
}

# CloudWatch Logs subscription filter
resource "aws_cloudwatch_log_subscription_filter" "security_filter" {
  name            = "security-log-filter"
  log_group_name  = "/aws/lambda/security-functions"
  filter_pattern  = "[timestamp, request_id, level=\"ERROR\"]"
  destination_arn = aws_kinesis_stream.security_logs.arn
  role_arn        = aws_iam_role.cloudwatch_role.arn
}
