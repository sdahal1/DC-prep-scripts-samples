import boto3

def audit_s3_buckets():
    """
    Audits all S3 buckets in an AWS account for public access.
    """
    # Create an S3 client to interact with the service
    s3_client = boto3.client('s3')
    
    # Get a list of all buckets in the account
    response = s3_client.list_buckets()
    buckets = response['Buckets']

    print("Starting S3 public access audit...")
    public_buckets = []
    
    # Loop through each bucket to check its settings
    for bucket in buckets:
        bucket_name = bucket['Name']
        is_public = False

        # Check for Public Access Block settings
        try:
            public_access_block = s3_client.get_public_access_block(Bucket=bucket_name)
            block_config = public_access_block['PublicAccessBlockConfiguration']
            if block_config['BlockPublicAcls'] or block_config['BlockPublicPolicy'] or \
               block_config['IgnorePublicAcls'] or block_config['RestrictPublicBuckets']:
                # The bucket has a public access block, so it's likely not public.
                # However, it could still have a policy that allows access from specific,
                # trusted public principals. We'll still check the policy below to be sure.
                pass
            else:
                is_public = True
        except s3_client.exceptions.NoSuchPublicAccessBlockConfiguration:
            # No public access block is configured, which is a security risk.
            is_public = True
        
        # Check the bucket policy for public access statements
        try:
            bucket_policy = s3_client.get_bucket_policy(Bucket=bucket_name)
            policy_json = bucket_policy['Policy']
            if '"Effect": "Allow", "Principal": "*"' in policy_json or '"Effect": "Allow", "Principal": {"AWS": "*"}' in policy_json:
                is_public = True
        except s3_client.exceptions.NoSuchBucketPolicy:
            # No bucket policy is a good sign (for this check), but doesn't guarantee security.
            pass

        if is_public:
            public_buckets.append(bucket_name)

    if public_buckets:
        print("\nFound the following potentially public buckets:")
        for bucket in public_buckets:
            print(f"- {bucket}")
    else:
        print("\nNo publicly accessible buckets found.")

# Run the audit
# audit_s3_buckets()