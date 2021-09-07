import botocore
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def list_log_streams(logs_client, log_group_name):
    try:
        response = logs_client.describe_log_streams(
            logGroupName=log_group_name,
            orderBy='LastEventTime',
            descending=True,
            limit=10
        )
        return response
    except botocore.exceptions.ClientError as error:
        logger.exception("There was an error: %s",
                         error.response['Error']['Code'])
        logger.exception(error.response['Error']['Message'])
        raise error


def list_logs_events(logs_client, log_group_name):
    logs_streams = list_log_streams(logs_client, log_group_name)['logStreams']
    try:
        if len(logs_streams) > 0:
            response = logs_client.get_log_events(
                logGroupName=log_group_name,
                logStreamName=logs_streams[0]['logStreamName'],
                startFromHead=False
            )
            return response
        else:
            return {'status': 404, 'message': 'There was not logs streams for this group name'}
    except botocore.exceptions.ClientError as error:
        logger.exception("There was an error: %s",
                         error.response['Error']['Code'])
        logger.exception(error.response['Error']['Message'])
        raise error


def list_lambda_functions(lambda_client):
    try:
        paginator = lambda_client.get_paginator('list_functions')
        lambda_list = []
        for response in paginator.paginate(PaginationConfig={
            'MaxItems': 300,
            'PageSize': 20
        }):
            for l in response.get('Functions', []):
                lambda_list.append(l)
        return lambda_list
    except botocore.exceptions.ClientError as error:
        logger.exception("There was an error: %s.", error)
        raise


def get_lambda_info(lambda_client, lambda_name):
    lambda_list = list_lambda_functions(lambda_client)
    for l in lambda_list:
        if l['FunctionName'] == lambda_name:
            return l
    return 'This lambda function does not exist in this region: {}'.format(lambda_name)
