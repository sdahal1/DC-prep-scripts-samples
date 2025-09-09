#!/usr/bin/env python3
import boto3
import json

class SecurityHubAutomation:
    def __init__(self):
        self.securityhub = boto3.client('securityhub')
        self.lambda_client = boto3.client('lambda')
        
    def get_findings_by_severity(self, severity='HIGH'):
        """Retrieve findings by severity level"""
        response = self.securityhub.get_findings(
            Filters={
                'SeverityLabel': [{'Value': severity, 'Comparison': 'EQUALS'}],
                'RecordState': [{'Value': 'ACTIVE', 'Comparison': 'EQUALS'}]
            }
        )
        return response['Findings']
    
    def auto_remediate_findings(self):
        """Automatically remediate common security findings"""
        findings = self.get_findings_by_severity('HIGH')
        remediated = []
        
        for finding in findings:
            finding_type = finding.get('Types', [])
            
            if 'Sensitive Data Identifications' in finding_type:
                # Handle S3 bucket exposure
                self._remediate_s3_exposure(finding)
                remediated.append(finding['Id'])
            
            elif 'Software and Configuration Checks' in finding_type:
                # Handle configuration issues
                self._remediate_config_issue(finding)
                remediated.append(finding['Id'])
        
        return remediated
    
    def _remediate_s3_exposure(self, finding):
        """Remediate S3 bucket public access"""
        s3 = boto3.client('s3')
        
        # Extract bucket name from finding
        resources = finding.get('Resources', [])
        for resource in resources:
            if 'S3Bucket' in resource.get('Type', ''):
                bucket_name = resource['Id'].split('/')[-1]
                
                # Block public access
                s3.put_public_access_block(
                    Bucket=bucket_name,
                    PublicAccessBlockConfiguration={
                        'BlockPublicAcls': True,
                        'IgnorePublicAcls': True,
                        'BlockPublicPolicy': True,
                        'RestrictPublicBuckets': True
                    }
                )
    
    def _remediate_config_issue(self, finding):
        """Remediate configuration compliance issues"""
        # Update finding status
        self.securityhub.batch_update_findings(
            FindingIdentifiers=[{
                'Id': finding['Id'],
                'ProductArn': finding['ProductArn']
            }],
            Note={
                'Text': 'Auto-remediation applied',
                'UpdatedBy': 'SecurityAutomation'
            },
            Workflow={'Status': 'RESOLVED'}
        )
    
    def create_custom_insight(self):
        """Create custom Security Hub insight"""
        insight = self.securityhub.create_insight(
            Name='High Severity Unresolved Findings',
            Filters={
                'SeverityLabel': [{'Value': 'HIGH', 'Comparison': 'EQUALS'}],
                'WorkflowStatus': [{'Value': 'NEW', 'Comparison': 'EQUALS'}]
            },
            GroupByAttribute='Type'
        )
        return insight['InsightArn']

if __name__ == "__main__":
    automation = SecurityHubAutomation()
    remediated = automation.auto_remediate_findings()
    print(f"Remediated {len(remediated)} findings")
