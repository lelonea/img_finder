import logging
import os

import boto3

def list_s3_objects(bucket_name, prefix='', region_name='eu-west-1'):
    """
    List all objects in a public S3 bucket with a given prefix.
    Returns a list of dictionaries containing object keys and URLs.
    """
    # Initialize the S3 client with specified credentials
    s3_client = boto3.client('s3',
                             region_name=region_name,
                             aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                             aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))

    logging.info(f"Listing objects in bucket {bucket_name} with prefix '{prefix}'")

    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

        objects = []
        if 'Contents' in response:
            for obj in response['Contents']:
                # Check for specific image file extensions
                if obj['Key'].endswith(('.jpg', '.jpeg', '.png', '.svg')):
                    object_url = f"https://{bucket_name}.s3.{region_name}.amazonaws.com/{obj['Key']}"
                    objects.append({'key': obj['Key'], 'url': object_url})

        logging.info(f"Found {len(objects)} objects in bucket {bucket_name} with prefix '{prefix}'")
        return objects
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return []

