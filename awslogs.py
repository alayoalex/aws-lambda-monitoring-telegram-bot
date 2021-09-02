import botocore.exceptions as ClientError
import boto3
import json
import logging
import os
from dotenv import load_dotenv

load_dotenv()

aws_access_key_id = os.environ['aws_access_key_id']
aws_secret_access_key = os.environ['aws_secret_access_key']
region = os.environ['aws_region']

session = boto3.Session(aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key,
                        region_name=region)
logs_client = session.client('logs')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def list_log_streams(log_group_name):
    try:
        response = logs_client.describe_log_streams(
            logGroupName=log_group_name,
            orderBy='LastEventTime',
            descending=True,
            limit=10
        )
        return response
    except ClientError as error:
        logger.exception("There was an error: %s",
                         error.response['Error']['Code'])
        logger.exception(error.response['Error']['Message'])
        raise error


def list_logs_events(log_group_name):
    logs_streams = list_log_streams(log_group_name)['logStreams']
    try:
        response = logs_client.get_log_events(
            logGroupName=log_group_name,
            logStreamName=logs_streams[0]['logStreamName'],
            startFromHead=False
        )
        return response
    except ClientError as error:
        logger.exception("There was an error: %s",
                         error.response['Error']['Code'])
        logger.exception(error.response['Error']['Message'])
        raise error
