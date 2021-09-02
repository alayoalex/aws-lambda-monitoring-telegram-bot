import logging
import os
import json
import awslogs
import utils
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


def start(update, context):
    update.effective_message.reply_text("Hi!")


# def echo(update, context):
#     update.effective_message.reply_text(update.effective_message.text)


def logs(update, context):
    response = json.dumps(awslogs.list_logs_events(
        "/aws/lambda/{}".format(context.args[0])), indent=4)
    if len(response) > 4096:
        for x in range(0, len(response), 4096):
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=response[x:x+4096])
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=response)


def ld(update, context):
    lambdas = awslogs.list_lambda_functions()
    for l in lambdas:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=l['FunctionName'])


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Sorry, I didn't understand that command.")


if __name__ == "__main__":
    # Set these variable to the appropriate values
    TOKEN = "1692535363:AAGDJzQlPMf-h7HU0lpEonxnYQlb3JCfG8I"
    NAME = "mizpa-telegram-bot"

    # Port is given by Heroku
    PORT = os.environ.get('PORT')

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
