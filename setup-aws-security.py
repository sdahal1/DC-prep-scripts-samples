#!/usr/bin/env python3
import boto3
import json

def setup_security_services():
    """Enable core AWS security services for practice"""
    
    # Initialize clients
    guardduty = boto3.client('guardduty', region_name='us-east-1')
    securityhub = boto3.client('securityhub', region_name='us-east-1')
    config = boto3.client('config', region_name='us-east-1')
    
    print("Setting up AWS Security Services...")
    
    # Enable GuardDuty
    try:
        detector = guardduty.create_detector(Enable=True)
        print(f"✓ GuardDuty enabled: {detector['DetectorId']}")
    except Exception as e:
        print(f"GuardDuty setup: {e}")
    
    # Enable Security Hub
    try:
        securityhub.enable_security_hub()
        print("✓ Security Hub enabled")
    except Exception as e:
        print(f"Security Hub setup: {e}")
    
    # Check CloudTrail
    cloudtrail = boto3.client('cloudtrail', region_name='us-east-1')
    try:
        trails = cloudtrail.describe_trails()
        if trails['trailList']:
            print(f"✓ CloudTrail active: {len(trails['trailList'])} trails")
        else:
            print("⚠ No CloudTrail found - consider enabling")
    except Exception as e:
        print(f"CloudTrail check: {e}")

if __name__ == "__main__":
    setup_security_services()
