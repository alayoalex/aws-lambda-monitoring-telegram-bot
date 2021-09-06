import botocore.exceptions as ClientError
import boto3
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AWS_Services:
    def __init__(self, aws_access_key_id, aws_secret_access_key, region):
        self.region = region
        self.session = boto3.Session(aws_access_key_id=aws_access_key_id,
                                     aws_secret_access_key=aws_secret_access_key,
                                     region_name=region)
        self.logs_client = self.session.client('logs')
        self.lambda_client = self.session.client('lambda')

    def list_log_streams(self, log_group_name):
        try:
            response = self.logs_client.describe_log_streams(
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

    def list_logs_events(self, log_group_name):
        logs_streams = self.list_log_streams(log_group_name)['logStreams']
        try:
            response = self.logs_client.get_log_events(
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

    def list_lambda_functions(self):
        try:
            paginator = self.lambda_client.get_paginator('list_functions')
            lambda_list = []
            for response in paginator.paginate(PaginationConfig={
                'MaxItems': 300,
                'PageSize': 20
            }):
                for l in response.get('Functions', []):
                    lambda_list.append(l)
            return lambda_list
        except ClientError as error:
            logger.exception("There was an error: %s.", error)
            raise

    def get_lambda_info(self, lambda_name):
        lambda_list = self.list_lambda_functions()
        for l in lambda_list:
            if l['FunctionName'] == lambda_name:
                return l
