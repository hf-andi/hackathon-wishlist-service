"""
TODO:
- Handle post request
- Save the image to S3
- Review confidence threshold for custom labels (currently 50%)

Needs to receive the following data from the POST request:
- File name
- image data
- User uuid
"""

import json
import boto3
import os

AWS_SERVER_PUBLIC_KEY = os.environ["AWS_SERVER_PUBLIC_KEY"]
AWS_SERVER_SECRET_KEY = os.environ["AWS_SERVER_SECRET_KEY"]
SQS_QUEUE_URL = os.environ["SQS_QUEUE_URL"]
REKOGNITION_MODEL_ARN = os.environ["REKOGNITION_MODEL_ARN"]
S3_BUCKET_NAME = os.environ["S3_BUCKET_NAME"]
S3_USER_UPLOADS_FOLDER = "user-uploads/"

rekognition = boto3.client(
    "rekognition",
    aws_access_key_id=AWS_SERVER_PUBLIC_KEY,
    aws_secret_access_key=AWS_SERVER_SECRET_KEY,
)
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_SERVER_PUBLIC_KEY,
    aws_secret_access_key=AWS_SERVER_SECRET_KEY,
)
sqs = boto3.client(
    "sqs",
    aws_access_key_id=AWS_SERVER_PUBLIC_KEY,
    aws_secret_access_key=AWS_SERVER_SECRET_KEY,
)


def push_to_s3(file_key: str):
    ...


def get_custom_labels_from_rekognition(file_key: str):
    file_obj = s3.get_object(Bucket=S3_BUCKET_NAME, Key=file_key)
    file_obj["Body"].read()

    try:
        label_data = rekognition.detect_custom_labels(
            ProjectVersionArn=REKOGNITION_MODEL_ARN,
            Image={"S3Object": {"Bucket": S3_BUCKET_NAME, "Name": file_key}},
            MinConfidence=50,
        )
        labels = label_data["CustomLabels"]
    except Exception as e:
        print("Error fetching custom labels for image", e)

    return labels


def push_custom_labels_to_sqs(user_uuid: str, file_key: str, labels: list):
    data_to_send = {"user_uuid": user_uuid, "s3_file_key": file_key, "labels": labels}
    sqs.send_message(QueueUrl=SQS_QUEUE_URL, MessageBody=json.dumps(data_to_send))


def lambda_handler(event, context):
    # Hardcoded values for now to test
    # Should get real file name and uuid from POST request
    # print(event['image'])
    # file_name = "image9.jpg"
    file_name = event["image"]
    user_uuid = "985d50c3-7347-472f-8e33-9cd3b1f39722"
    file_key = S3_USER_UPLOADS_FOLDER + file_name

    push_to_s3(file_key)

    labels = get_custom_labels_from_rekognition(file_key)
    print(labels)

    push_custom_labels_to_sqs(user_uuid, file_key, labels)

    return {"statusCode": 200, "body": json.dumps("Hello from Lambda!")}
