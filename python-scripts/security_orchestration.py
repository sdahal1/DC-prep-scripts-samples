#!/usr/bin/env python3
import boto3
import json
import time
from concurrent.futures import ThreadPoolExecutor

class SecurityOrchestrator:
    def __init__(self):
        self.session = boto3.Session()
        self.regions = ['us-east-1', 'us-west-2', 'eu-west-1']
        
    def multi_region_security_scan(self):
        """Perform security scan across multiple regions"""
        results = {}
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(self._scan_region, region): region 
                for region in self.regions
            }
            
            for future in futures:
                region = futures[future]
                try:
                    results[region] = future.result()
                except Exception as e:
                    results[region] = {'error': str(e)}
        
        return results
    
    def _scan_region(self, region):
        """Scan security posture in specific region"""
        ec2 = self.session.client('ec2', region_name=region)
        s3 = self.session.client('s3', region_name=region)
        
        findings = {
            'security_groups': self._check_security_groups(ec2),
            'instances': self._check_instances(ec2),
            'volumes': self._check_volumes(ec2)
        }
        
        return findings
    
    def _check_security_groups(self, ec2):
        """Check security group configurations"""
        findings = []
        sgs = ec2.describe_security_groups()['SecurityGroups']
        
        for sg in sgs:
            # Check for overly permissive rules
            for rule in sg.get('IpPermissions', []):
                if any(ip.get('CidrIp') == '0.0.0.0/0' for ip in rule.get('IpRanges', [])):
                    findings.append({
                        'type': 'OPEN_SECURITY_GROUP',
                        'resource': sg['GroupId'],
                        'port': rule.get('FromPort', 'All'),
                        'protocol': rule.get('IpProtocol', 'All')
                    })
        
        return findings
    
    def _check_instances(self, ec2):
        """Check EC2 instance security"""
        findings = []
        instances = ec2.describe_instances()
        
        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                # Check for instances without proper tags
                tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                
                if 'Environment' not in tags or 'Owner' not in tags:
                    findings.append({
                        'type': 'MISSING_TAGS',
                        'resource': instance['InstanceId'],
                        'state': instance['State']['Name']
                    })
                
                # Check for instances in public subnets
                if instance.get('PublicIpAddress'):
                    findings.append({
                        'type': 'PUBLIC_INSTANCE',
                        'resource': instance['InstanceId'],
                        'public_ip': instance['PublicIpAddress']
                    })
        
        return findings
    
    def _check_volumes(self, ec2):
        """Check EBS volume encryption"""
        findings = []
        volumes = ec2.describe_volumes()['Volumes']
        
        for volume in volumes:
            if not volume.get('Encrypted', False):
                findings.append({
                    'type': 'UNENCRYPTED_VOLUME',
                    'resource': volume['VolumeId'],
                    'size': volume['Size']
                })
        
        return findings
    
    def auto_remediate(self, findings):
        """Automatically remediate security findings"""
        remediation_results = []
        
        for region, region_findings in findings.items():
            ec2 = self.session.client('ec2', region_name=region)
            
            for finding_type, finding_list in region_findings.items():
                if finding_type == 'security_groups':
                    for finding in finding_list:
                        if finding['type'] == 'OPEN_SECURITY_GROUP':
                            # Create restricted security group rule
                            result = self._restrict_security_group(ec2, finding)
                            remediation_results.append(result)
        
        return remediation_results
    
    def _restrict_security_group(self, ec2, finding):
        """Restrict overly permissive security group"""
        try:
            # This would typically involve more sophisticated logic
            # For demo purposes, we'll just log the action
            return {
                'action': 'RESTRICT_SG',
                'resource': finding['resource'],
                'status': 'SUCCESS',
                'message': f"Would restrict access for {finding['resource']}"
            }
        except Exception as e:
            return {
                'action': 'RESTRICT_SG',
                'resource': finding['resource'],
                'status': 'FAILED',
                'error': str(e)
            }

if __name__ == "__main__":
    orchestrator = SecurityOrchestrator()
    scan_results = orchestrator.multi_region_security_scan()
    print(json.dumps(scan_results, indent=2, default=str))
