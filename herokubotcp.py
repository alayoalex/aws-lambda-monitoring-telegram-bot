import logging
import os
from queue import Queue

import cherrypy
import telegram
from telegram.ext import CommandHandler, MessageHandler, Filters, Dispatcher


class SimpleWebsite:
    @cherrypy.expose
    def index(self):
        return """<H1>Welcome!</H1>"""


class BotComm:
    exposed = True

    def __init__(self, TOKEN, NAME):
        super().__init__()
        self.TOKEN = TOKEN
        self.NAME = NAME
        self.bot = telegram.Bot(self.TOKEN)
        try:
            self.bot.set_webhook(
                f"https://{self.NAME}.herokuapp.com/{self.TOKEN}")
        except:
            raise RuntimeError("Failed to set the webhook")

        self.update_queue = Queue()
        self.dp = Dispatcher(self.bot, self.update_queue)

        self.dp.add_handler(CommandHandler("start", self._start))
        self.dp.add_handler(MessageHandler(
            Filters.text & ~Filters.command, self._echo))

    @cherrypy.tools.json_in()
    def POST(self, *args, **kwargs):
        update = cherrypy.request.json
        update = telegram.Update.de_json(update, self.bot)
        self.dp.process_update(update)

    def _start(self, update, context):
        update.effective_message.reply_text("Hi!")

    def _echo(self, update, context):
        update.effective_message.reply_text(update.effective_message.text)


if __name__ == "__main__":
    # Set these variable to the appropriate values
    TOKEN = "bot1692535363:AAGDJzQlPMf-h7HU0lpEonxnYQlb3JCfG8I"
    NAME = "mizpa-telegram-bot"

    # Port is given by Heroku
    PORT = os.environ.get('PORT')

    # Enable logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Set up the cherrypy configuration
    cherrypy.config.update({'server.socket_host': '0.0.0.0', })
    cherrypy.config.update({'server.socket_port': int(PORT), })
    cherrypy.tree.mount(SimpleWebsite(), "/")
    cherrypy.tree.mount(BotComm(TOKEN, NAME),
                        "/{}".format(TOKEN),
                        {'/': {'request.dispatch': cherrypy.dispatch.MethodDispatcher()}})
    cherrypy.engine.start()
