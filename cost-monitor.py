#!/usr/bin/env python3
import boto3
from datetime import datetime, timedelta

def check_security_service_costs():
    """Monitor costs for security services"""
    ce = boto3.client('ce', region_name='us-east-1')
    
    # Get costs for last 7 days
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    try:
        response = ce.get_cost_and_usage(
            TimePeriod={'Start': start_date, 'End': end_date},
            Granularity='DAILY',
            Metrics=['BlendedCost'],
            GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
        )
        
        print("Security Service Costs (Last 7 days):")
        for result in response['ResultsByTime']:
            date = result['TimePeriod']['Start']
            print(f"\nDate: {date}")
            
            for group in result['Groups']:
                service = group['Keys'][0]
                cost = float(group['Metrics']['BlendedCost']['Amount'])
                
                if any(svc in service.lower() for svc in ['guardduty', 'security', 'config']):
                    print(f"  {service}: ${cost:.4f}")
                    
    except Exception as e:
        print(f"Cost monitoring error: {e}")
        print("Note: Cost data may take 24-48 hours to appear")

def disable_expensive_services():
    """Disable services to minimize costs"""
    print("\nCost Optimization Options:")
    print("1. Keep GuardDuty (essential for practice) - ~$4/month")
    print("2. Keep Security Hub (minimal cost) - ~$0.10/month") 
    print("3. Disable both services when not actively practicing")
    
    choice = input("\nDisable services now? (y/n): ")
    if choice.lower() == 'y':
        # Disable GuardDuty
        guardduty = boto3.client('guardduty', region_name='us-east-1')
        detectors = guardduty.list_detectors()['DetectorIds']
        
        for detector_id in detectors:
            guardduty.update_detector(DetectorId=detector_id, Enable=False)
            print(f"✓ GuardDuty detector {detector_id} disabled")
        
        # Disable Security Hub
        securityhub = boto3.client('securityhub', region_name='us-east-1')
        try:
            securityhub.disable_security_hub()
            print("✓ Security Hub disabled")
        except Exception as e:
            print(f"Security Hub disable: {e}")

if __name__ == "__main__":
    check_security_service_costs()
    disable_expensive_services()
