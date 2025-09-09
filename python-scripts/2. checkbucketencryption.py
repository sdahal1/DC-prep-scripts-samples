import boto3
from botocore.exceptions import ClientError

def check_bucket_encryption(bucket_name):
    s3_client = boto3.client('s3')
    
    try:
        # This will succeed if the bucket has server-side encryption enabled
        s3_client.get_bucket_encryption(Bucket=bucket_name)
        print(f"✅ Bucket '{bucket_name}' has encryption enabled.")
        return True
    except ClientError as e:
        # This block will run if the API call fails
        if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
            print(f"❌ Bucket '{bucket_name}' is NOT encrypted.")
            return False
        else:
            # Handle any other, unexpected errors
            print(f"⚠️ An unexpected error occurred: {e}")
            return False

# Example usage:
# Check a bucket that is encrypted
# check_bucket_encryption('my-encrypted-bucket')

# Check a bucket that is not encrypted
# check_bucket_encryption('my-unencrypted-bucket')
