#!/usr/bin/env python3
import boto3
import json
from datetime import datetime

class IncidentResponse:
    def __init__(self):
        self.ec2 = boto3.client('ec2')
        self.iam = boto3.client('iam')
        self.sns = boto3.client('sns')
        
    def isolate_instance(self, instance_id):
        """Isolate compromised EC2 instance"""
        # Create isolation security group
        isolation_sg = self.ec2.create_security_group(
            GroupName=f'isolation-{instance_id}',
            Description='Isolation security group for incident response'
        )
        
        # Modify instance security groups
        self.ec2.modify_instance_attribute(
            InstanceId=instance_id,
            Groups=[isolation_sg['GroupId']]
        )
        
        return isolation_sg['GroupId']
    
    def disable_user_access(self, username):
        """Disable compromised user access"""
        # Attach deny-all policy
        deny_policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Deny",
                "Action": "*",
                "Resource": "*"
            }]
        }
        
        self.iam.put_user_policy(
            UserName=username,
            PolicyName='IncidentResponseDeny',
            PolicyDocument=json.dumps(deny_policy)
        )
        
        # Deactivate access keys
        keys = self.iam.list_access_keys(UserName=username)
        for key in keys['AccessKeyMetadata']:
            self.iam.update_access_key(
                UserName=username,
                AccessKeyId=key['AccessKeyId'],
                Status='Inactive'
            )
    
    def create_forensic_snapshot(self, instance_id):
        """Create forensic snapshot of instance volumes"""
        instance = self.ec2.describe_instances(InstanceIds=[instance_id])
        volumes = []
        
        for reservation in instance['Reservations']:
            for inst in reservation['Instances']:
                for bdm in inst.get('BlockDeviceMappings', []):
                    volume_id = bdm['Ebs']['VolumeId']
                    snapshot = self.ec2.create_snapshot(
                        VolumeId=volume_id,
                        Description=f'Forensic snapshot for incident {datetime.now().isoformat()}'
                    )
                    volumes.append(snapshot['SnapshotId'])
        
        return volumes
    
    def notify_stakeholders(self, incident_details):
        """Send incident notification"""
        message = {
            'incident_id': incident_details.get('id'),
            'severity': incident_details.get('severity'),
            'description': incident_details.get('description'),
            'timestamp': datetime.now().isoformat(),
            'actions_taken': incident_details.get('actions', [])
        }
        
        # Send to SNS topic (configure topic ARN)
        # self.sns.publish(
        #     TopicArn='arn:aws:sns:region:account:incident-notifications',
        #     Message=json.dumps(message),
        #     Subject=f"Security Incident: {incident_details.get('severity')}"
        # )
        
        return message

if __name__ == "__main__":
    ir = IncidentResponse()
    # Example usage
    incident = {
        'id': 'INC-001',
        'severity': 'HIGH',
        'description': 'Suspicious activity detected on EC2 instance',
        'actions': ['Instance isolated', 'Forensic snapshot created']
    }
    print(json.dumps(ir.notify_stakeholders(incident), indent=2))
