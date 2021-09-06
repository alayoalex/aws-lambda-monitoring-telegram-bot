import logging
import os
import json
import awslogs
import utils
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


aws_access_key_id = os.environ['aws_access_key_id']
aws_secret_access_key = os.environ['aws_secret_access_key']
region = os.environ['region']

regions = ['us-east-1', 'us-east-2']


def start(update, context):
    update.effective_message.reply_text("Hi!")


# def echo(update, context):
#     update.effective_message.reply_text(update.effective_message.text)


def logs(update, context):
    aws_logs = awslogs.AWS_Services(
        aws_secret_access_key, aws_secret_access_key, region)
    response = json.dumps(aws_logs.list_logs_events(
        "/aws/lambda/{}".format(context.args[0])), indent=4)
    if len(response) > 4096:
        for x in range(0, len(response), 4096):
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=response[x:x+4096])
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=response)


def ld(update, context):
    """
    Commands
    /ld: get all function names, default region us-east-2
    /ld [region]: get all function names of a specific region 
    /ld [function_name]: get a function metadata, default region us-east-2
    /ld [region] [function_name]: get a function metadata of a specific region
    """
    if len(context.args) > 0:
        if context.args[0].split('=')[0] == 'region':
            aws_logs = awslogs.AWS_Services(
                aws_secret_access_key, aws_secret_access_key, context.args[0].split('=')[1])
        else:
            aws_logs = awslogs.AWS_Services(
                aws_secret_access_key, aws_secret_access_key, region)

    if len(context.args) == 0:
        aws_logs = awslogs.AWS_Services(
            aws_secret_access_key, aws_secret_access_key, region)
        lambdas = aws_logs.list_lambda_functions()
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
        lambda_f = json.dumps(
            aws_logs.get_lambda_info(context.args[0]), indent=4)
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=lambda_f)
    elif len(context.args) == 2:
        lambda_f = json.dumps(
            aws_logs.get_lambda_info(context.args[1]), indent=4)
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=lambda_f)


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Sorry, I didn't understand that command.")


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
    dp.add_handler(MessageHandler(Filters.command, unknown))

    # Start the webhook
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN,
                          webhook_url=f"https://{NAME}.herokuapp.com/{TOKEN}")
    updater.idle()
