from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

line_bot_api = LineBotApi('S1wOAMvKReHOn77NGBxEpdCuTrZE6Hbgq5HY1LJFJjkVPc+viYd6YEdgp7zwDjEpNTiS/A6Q8MBznQoWT6zod4e1kZt3C4Z0GaOFFUshvxZ5PXcnJXJsbjhLRCX+UNzq9YMNXbkFGdgUmIu+010bLwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('e2d100457f5d41dc8db8415f8c0b8e16')


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))


if __name__ == "__main__":
    app.run()