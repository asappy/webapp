
from flask import Flask, request, abort
import os

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, QuickReplyButton, MessageAction, QuickReply,
)
import requests
import json
import time
import base64
import hmac
import hashlib

app = Flask(__name__)

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["LINE_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["LINE_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

auth_key = os.environ["SWITCHBOT_AUTH_KEY"] # copy and paste from the SwitchBot app V6.14 or later
secret = os.environ["SWITCHBOT_SECRET"] # copy and paste from the SwitchBot app V6.14 or later
def generate_sign(token: str, secret: str, nonce: str) -> tuple[str, str]:
    """SWITCH BOT APIの認証キーを生成する"""

    t = int(round(time.time() * 1000))
    string_to_sign = "{}{}{}".format(token, t, nonce)
    string_to_sign_b = bytes(string_to_sign, "utf-8")
    secret_b = bytes(secret, "utf-8")
    sign = base64.b64encode(
        hmac.new(secret_b, msg=string_to_sign_b, digestmod=hashlib.sha256).digest()
    )

    return (str(t), str(sign, "utf-8"))

def operate_switchobot_turnOff(ID, times):
    url = "https://api.switch-bot.com/v1.1/devices/" + ID + "/commands"
    nonce = "zzz"
    t, sign = generate_sign(auth_key, secret, nonce)
    headers = {
        "Content-Type": "application/json; charset: utf8",
        "Authorization": auth_key,
        "t": t,
        "sign": sign,
        "nonce": nonce,
    }

    params = {
    "command": "turnOff",
    "parameter": "default",
    "commandType": "command"
    }
    r = requests.post(url, headers=headers, data=json.dumps(params))
    if times == 2:
        time.sleep(1)
        r = requests.post(url, headers=headers, data=json.dumps(params))
    return

def operate_switchobot_turnOn(ID):
    url = "https://api.switch-bot.com/v1.1/devices/" + ID + "/commands"
    nonce = "zzz"
    t, sign = generate_sign(auth_key, secret, nonce)
    headers = {
        "Content-Type": "application/json; charset: utf8",
        "Authorization": auth_key,
        "t": t,
        "sign": sign,
        "nonce": nonce,
    }

    params = {
    "command": "turnOn",
    "parameter": "default",
    "commandType": "command"
    }
    r = requests.post(url, headers=headers, data=json.dumps(params))
    return

@app.route("/")
def hello_world():
    return "hello world!"#テスト用

@app.route("/webhook", methods=['POST'])
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
    language_list = ["エアコン", "照明オン", "照明オフ", "テレビオン", "テレビオフ"]
    device_id_light = "02-202207132247-89473231"
    device_id_airconditioner = "02-202207132236-15163498"
    device_id_tv = "02-202207132329-83831759"
    gettext = event.message.text
    if gettext == "あ" or gettext == "、":
        items = [QuickReplyButton(action=MessageAction(label=f"{language}", text=f"{language}")) for language in language_list]

        messages = TextSendMessage(text="操作する機器",
                                    quick_reply=QuickReply(items=items))
        
        line_bot_api.reply_message(event.reply_token, messages=messages)
    elif gettext == "照明オン":

        operate_switchobot_turnOn(device_id_light)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="照明をつけました。"))
    elif gettext == "照明オフ":
        operate_switchobot_turnOff(device_id_light, 2)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="照明を消しました。"))
    elif gettext == "エアコン":
        operate_switchobot_turnOff(device_id_airconditioner, 1)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="エアコンを消しました。"))        
    elif gettext == "テレビオン":
        operate_switchobot_turnOn(device_id_tv)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="テレビをつけました。"))
    elif gettext == "テレビオフ":
        operate_switchobot_turnOff(device_id_tv, 1)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="テレビを消しました。"))       
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text))

if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)