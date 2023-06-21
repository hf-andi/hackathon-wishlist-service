import json
import os
import package.boto3 as boto3
import package.psycopg2 as psycopg2

AWS_SERVER_PUBLIC_KEY = os.environ["AWS_SERVER_PUBLIC_KEY"]
AWS_SERVER_SECRET_KEY = os.environ["AWS_SERVER_SECRET_KEY"]

def extract_s3_bucket_and_filekey_from_sqs_event(event):
    """
    Extracts the bucket name and file key string from an SQS message
    :param queue_name: SQS message
    :return: bucket_name, filekey string tuple
    """

    msg = json.loads(event["Records"][0]["body"])
    msg = msg["Records"][0]["s3"]

    return msg["bucket"]["name"], msg["object"]["key"]


def lambda_handler(event, context):

    print("EVENT", event)

    bucket_name, filekey = extract_s3_bucket_and_filekey_from_sqs_event(event)

    client = boto3.client(
        "rekognition",
        aws_access_key_id=AWS_SERVER_PUBLIC_KEY,
        aws_secret_access_key=AWS_SERVER_SECRET_KEY,
    )

    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_SERVER_PUBLIC_KEY,
        aws_secret_access_key=AWS_SERVER_SECRET_KEY,
    )
    fileObj = s3.get_object(Bucket=bucket_name, Key=filekey)
    fileObj["Body"].read()
    response = client.detect_labels(
        Image={"S3Object": {"Bucket": bucket_name, "Name": filekey}}, MaxLabels=3, MinConfidence=70
    )
    print(response)

    return {"statusCode": 200, "body": json.dumps("Hello from Lambda!")}
