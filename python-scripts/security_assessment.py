#!/usr/bin/env python3
import boto3
import json
from datetime import datetime

class SecurityAssessment:
    def __init__(self):
        self.ec2 = boto3.client('ec2')
        self.s3 = boto3.client('s3')
        self.iam = boto3.client('iam')
        
    def check_security_groups(self):
        """Check for overly permissive security groups"""
        findings = []
        sgs = self.ec2.describe_security_groups()['SecurityGroups']
        
        for sg in sgs:
            for rule in sg.get('IpPermissions', []):
                for ip_range in rule.get('IpRanges', []):
                    if ip_range.get('CidrIp') == '0.0.0.0/0':
                        findings.append({
                            'type': 'SECURITY_GROUP_OPEN',
                            'resource': sg['GroupId'],
                            'severity': 'HIGH',
                            'description': f"Security group {sg['GroupId']} allows 0.0.0.0/0"
                        })
        return findings
    
    def check_s3_buckets(self):
        """Check S3 bucket security configurations"""
        findings = []
        buckets = self.s3.list_buckets()['Buckets']
        
        for bucket in buckets:
            bucket_name = bucket['Name']
            try:
                # Check public access
                public_access = self.s3.get_public_access_block(Bucket=bucket_name)
                if not public_access['PublicAccessBlockConfiguration']['BlockPublicAcls']:
                    findings.append({
                        'type': 'S3_PUBLIC_ACCESS',
                        'resource': bucket_name,
                        'severity': 'HIGH',
                        'description': f"Bucket {bucket_name} allows public ACLs"
                    })
            except:
                pass
        return findings
    
    def generate_report(self):
        """Generate comprehensive security assessment report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'findings': []
        }
        
        report['findings'].extend(self.check_security_groups())
        report['findings'].extend(self.check_s3_buckets())
        
        return report

if __name__ == "__main__":
    assessment = SecurityAssessment()
    report = assessment.generate_report()
    print(json.dumps(report, indent=2))
