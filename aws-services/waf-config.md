# AWS WAF v2 Configuration Documentation

## Overview
This Terraform configuration creates a comprehensive AWS WAF v2 Web ACL with multiple security layers for web application protection.

## Configuration Details

### Main Web ACL
- **Name:** security-web-acl
- **Scope:** REGIONAL
- **Default Action:** Allow (blocks only when rules match)

### Security Rules

#### 1. Rate Limiting Rule (Priority 1)
- **Action:** Block
- **Limit:** 2000 requests per 5-minute window per IP
- **Purpose:** Prevents DDoS and brute force attacks
- **Monitoring:** CloudWatch metrics enabled

#### 2. Common Rule Set (Priority 2)
- **Rule Set:** AWSManagedRulesCommonRuleSet
- **Action:** Override none (use rule group defaults)
- **Purpose:** Protects against OWASP Top 10 threats (XSS, directory traversal, etc.)
- **Monitoring:** CloudWatch metrics enabled

#### 3. SQL Injection Protection (Priority 3)
- **Rule Set:** AWSManagedRulesSQLiRuleSet
- **Action:** Override none (use rule group defaults)
- **Purpose:** Blocks malicious SQL injection attempts
- **Monitoring:** CloudWatch metrics enabled

## Monitoring & Visibility

All rules include:
- CloudWatch metrics enabled
- Sampled request logging for analysis
- Individual metric names for tracking

## Security Benefits

- **Multi-layered Protection:** Combines rate limiting with AWS managed rules
- **Automated Threat Detection:** Uses AWS managed rule sets for known attack patterns
- **DDoS Protection:** Rate limiting prevents abuse and volumetric attacks
- **Full Observability:** CloudWatch integration for monitoring and alerting
- **Production Ready:** Enterprise-grade configuration suitable for production environments

## Tags
- Environment: production
- Purpose: web-security
