# AWS WAF v2 Configuration - Creates a web security firewall
resource "aws_wafv2_web_acl" "security_acl" {
  name  = "security-web-acl"  # Give your firewall a name
  scope = "REGIONAL"          # Protects resources in one AWS region (like ALB, API Gateway)
  
  # Default behavior: allow all traffic unless a rule blocks it
  default_action {
    allow {}  # Let traffic through by default (only block when rules match)
  }
  
  # RULE 1: Rate limiting - stops too many requests from same IP
  rule {
    name     = "RateLimitRule"  # Name for this specific rule
    priority = 1               # Lower number = higher priority (checked first)
    
    # What to do when rule matches: block the request
    action {
      block {}  # Stop the request completely
    }
    
    # The actual rule logic: count requests per IP address
    statement {
      rate_based_statement {
        limit              = 2000  # Allow max 2000 requests per 5 minutes per IP
        aggregate_key_type = "IP"  # Count requests by IP address
      }
    }
    
    # Monitoring settings: track what this rule is doing
    visibility_config {
      cloudwatch_metrics_enabled = true           # Send metrics to CloudWatch
      metric_name                = "RateLimitRule" # Name for the metric
      sampled_requests_enabled   = true           # Log some blocked requests for analysis
    }
  }
  
  # RULE 2: AWS Managed Common Rules - blocks common web attacks
  rule {
    name     = "AWSManagedRulesCommonRuleSet"  # Use AWS's pre-built security rules
    priority = 2                              # Second priority (checked after rate limit)
    
    # Don't override AWS decisions - trust their expert recommendations
    override_action {
      none {}  # Use AWS's recommended actions (block/allow) without changes
    }
    
    # Tell WAF to use AWS's common attack protection rules
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"  # The specific AWS rule set to use
        vendor_name = "AWS"                          # Confirms this comes from AWS
      }
    }
    
    # Monitoring: track what common attacks are being blocked
    visibility_config {
      cloudwatch_metrics_enabled = true                    # Send metrics to CloudWatch
      metric_name                = "CommonRuleSetMetric"   # Name for tracking this rule
      sampled_requests_enabled   = true                    # Log some blocked attacks
    }
  }
  
  # RULE 3: SQL Injection protection - stops database attacks
  rule {
    name     = "AWSManagedRulesSQLiRuleSet"  # Use AWS's SQL injection protection
    priority = 3                            # Third priority (checked last)
    
    # Trust AWS experts - don't change their SQL injection decisions
    override_action {
      none {}  # Use AWS's recommended blocking actions
    }
    
    # Use AWS's specialized SQL injection detection rules
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesSQLiRuleSet"  # AWS's SQL injection rule set
        vendor_name = "AWS"                        # Confirms this is from AWS
      }
    }
    
    # Monitor SQL injection attempts
    visibility_config {
      cloudwatch_metrics_enabled = true                # Track SQL injection blocks
      metric_name                = "SQLiRuleSetMetric" # Metric name for this rule
      sampled_requests_enabled   = true                # Log some SQL injection attempts
    }
  }
  
  # Overall WAF monitoring settings
  visibility_config {
    cloudwatch_metrics_enabled = true            # Track overall WAF activity
    metric_name                = "SecurityWebACL" # Main metric name for this WAF
    sampled_requests_enabled   = true            # Log sample requests for analysis
  }
  
  # Labels for organization and billing
  tags = {
    Environment = "production"   # Mark this as production environment
    Purpose     = "web-security" # Identify this resource's purpose
  }
}
