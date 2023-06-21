import json
import os

import boto3
import psycopg2

AWS_SERVER_PUBLIC_KEY = os.environ["AWS_SERVER_PUBLIC_KEY"]
AWS_SERVER_SECRET_KEY = os.environ["AWS_SERVER_SECRET_KEY"]


def connect_to_db():
    try:
        conn = psycopg2.connect(
            host=os.environ["HOST"],
            database=os.environ["DB_NAME"],
            user=os.environ["USERNAME"],
            password=os.environ["PASSWORD"]
        )
        return conn.cursor()
    except Exception as e:
        print(e)
        print("can't connect to db for some reason")
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


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
    response = client.detect_custom_labels(
        ProjectVersionArn="""
            arn:aws:rekognition:ap-southeast-2:532495396307:project/wishlist-service/version/wishlist-service.2023-06-20T16.07.25/1687241245408
        """,
        Image={"S3Object": {"Bucket": bucket_name, "Name": filekey}},
        MinConfidence=70,
    )

    cur = connect_to_db()
    cur.execute('select * from recipes')
    print(response)

    return {"statusCode": 200, "body": json.dumps("Hello from Lambda!")}
