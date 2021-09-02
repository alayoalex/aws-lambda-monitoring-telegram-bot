import logging
import os
import awslogs
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


def start(update, context):
    update.effective_message.reply_text("Hi!")


def echo(update, context):
    update.effective_message.reply_text(update.effective_message.text)


def logs(update, context):
    text_caps = ' '.join(context.args).upper()
    context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)
    # response = awslogs.list_logs_events(
    #     "/aws/lambda/{}".format(update.effective_message.text))
    # update.effective_message.reply_text(response)


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
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the webhook
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN,
                          webhook_url=f"https://{NAME}.herokuapp.com/{TOKEN}")
    updater.idle()
