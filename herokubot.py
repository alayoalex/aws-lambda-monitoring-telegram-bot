import logging
import os
import json
import awslogs
# import utils
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import boto3


regions = ['us-east-1', 'us-east-2']

aws_access_key_id = os.environ['aws_access_key_id']
aws_secret_access_key = os.environ['aws_secret_access_key']
region = os.environ['region']


def start(update, context):
    update.effective_message.reply_text("Hi!")


def logs(update, context):
    """
    Commands
    /logs [function_name]: get a function logs, default region us-east-2
    /logs [region] [function_name]: get a function logs of a specific region
    """
    if len(context.args) == 1:
        session = boto3.Session(aws_access_key_id=aws_access_key_id,
                                aws_secret_access_key=aws_secret_access_key,
                                region_name=region)
        logs_client = session.client('logs')
        response = json.dumps(awslogs.list_logs_events(logs_client,
                                                       "/aws/lambda/{}".format(context.args[0])), indent=4)
        if len(response) > 4096:
            for x in range(0, len(response), 4096):
                context.bot.send_message(
                    chat_id=update.effective_chat.id, text=response[x:x+4096])
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=response)
    elif len(context.args) == 2:
        session = boto3.Session(aws_access_key_id=aws_access_key_id,
                                aws_secret_access_key=aws_secret_access_key,
                                region_name=context.args[0])
        logs_client = session.client('logs')
        response = json.dumps(awslogs.list_logs_events(logs_client,
                                                       "/aws/lambda/{}".format(context.args[1])), indent=4)
        if len(response) > 4096:
            for x in range(0, len(response), 4096):
                context.bot.send_message(
                    chat_id=update.effective_chat.id, text=response[x:x+4096])
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=response)
    else:
        message = 'Incorrect Command, please, check the bot help.'
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=message)


def ld(update, context):
    """
    Commands
    /ld: get all function names, default region us-east-2
    /ld [region]: get all function names of a specific region 
    /ld [function_name]: get a function metadata, default region us-east-2
    /ld [region] [function_name]: get a function metadata of a specific region
    """

    if len(context.args) == 0:
        session = boto3.Session(aws_access_key_id=aws_access_key_id,
                                aws_secret_access_key=aws_secret_access_key,
                                region_name=region)
        lambda_client = session.client('lambda')
        lambdas = awslogs.list_lambda_functions(lambda_client)
        text = "There are {} lambda functions in us-east-2 region.".format(
            len(lambdas))
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=text)
        names = []
        for l in lambdas:
            names.append(l['FunctionName'])
        names_str = "\n".join(names)
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=str(names_str))
    elif len(context.args) == 1:
        if context.args[0] in regions:
            session = boto3.Session(aws_access_key_id=aws_access_key_id,
                                    aws_secret_access_key=aws_secret_access_key,
                                    region_name=context.args[0])
            lambda_client = session.client('lambda')
            lambdas = awslogs.list_lambda_functions(lambda_client)
            text = "There are {} lambda functions in {} region.".format(
                len(lambdas), context.args[0])
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=text)
            names = []
            for l in lambdas:
                names.append(l['FunctionName'])
            names_str = "\n".join(names)
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=str(names_str))
        else:
            session = boto3.Session(aws_access_key_id=aws_access_key_id,
                                    aws_secret_access_key=aws_secret_access_key,
                                    region_name=region)
            lambda_client = session.client('lambda')
            lambda_f = json.dumps(
                awslogs.get_lambda_info(lambda_client, context.args[0]), indent=4)
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=lambda_f)
    elif len(context.args) == 2:
        if context.args[0] in regions:
            session = boto3.Session(aws_access_key_id=aws_access_key_id,
                                    aws_secret_access_key=aws_secret_access_key,
                                    region_name=context.args[0])
            lambda_client = session.client('lambda')
            lambda_f = json.dumps(
                awslogs.get_lambda_info(lambda_client, context.args[1]), indent=4)
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=lambda_f)
        else:
            message = 'This region does not exist: {}'.format(context.args[0])
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=message)
    else:
        message = 'Incorrect Command, please, check the bot help.'
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=message)


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Sorry, I didn't understand that command.")


def help_command(update, context):
    """Displays info on how to use the bot."""
    update.message.reply_text(
        """
        Commands
        /start to test and awake this bot
        /help to view commands
        /ld: get all function names, default region us-east-2
        /ld [region]: get all function names of a specific region
        /ld [function_name]: get a function metadata, default region us-east-2
        /ld [region] [function_name]: get a function metadata of a specific region
        /logs [function_name]: get a function logs, default region us-east-2
        /logs [region] [function_name]: get a function logs of a specific region \n
        Examples:
        /ld hello-world-function
        /ld us-east-1 hello-world-function
        /logs hello-world-function
        /logs us-east-1 hello-world-function
        """
    )


if __name__ == "__main__":
    # Set these variable to the appropriate values
    TOKEN = os.environ['TOKEN']
    # Port is given by Heroku
    PORT = os.environ.get('PORT')
    NAME = "mizpa-telegram-bot"

    # Enable logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Set up the Updater
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    # Add handlers
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('logs', logs))
    dp.add_handler(CommandHandler('ld', ld))
    dp.add_handler(CommandHandler('help', help_command))
    dp.add_handler(MessageHandler(Filters.command, unknown))

    # Start the webhook
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN,
                          webhook_url=f"https://{NAME}.herokuapp.com/{TOKEN}")
    updater.idle()
