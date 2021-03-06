import boto3
import os
from datetime import datetime 
s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
)

# session = boto3.Session( aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
# s3 = session.resource('s3')

def s3upload(file):
    split_filename = file.filename.split('.')
    dt = datetime.now()
    seq = dt.strftime("%m%d%Y-%H%M%S%f")
    finalfilename = split_filename[0] + '_' + seq + '.' + split_filename[1]
    s3_resource = boto3.resource('s3')
    my_bucket = s3_resource.Bucket(os.environ.get('AWS_BUCKET_NAME'))
    my_bucket.Object(finalfilename).put(Body=file, ACL='public-read',ContentType='image/jpeg')
    return f"https://{os.environ.get('AWS_BUCKET_NAME')}.s3-us-west-2.amazonaws.com/{finalfilename}"