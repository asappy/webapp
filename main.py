from flask import Flask
import os

import requests
import json
import time
import base64
import hmac
import hashlib

app = Flask(__name__)

auth_key = os.environ["SWITCHBOT_AUTH_KEY"] # copy and paste from the SwitchBot app V6.14 or later
secret = os.environ["SWITCHBOT_SECRET"] # copy and paste from the SwitchBot app V6.14 or later

device_id_light = "02-202207132247-89473231"
device_id_airconditioner = "02-202207132236-15163498"
device_id_tv = "02-202207132329-83831759"

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

def operate_switchobot_airconditioner_turnOn(ID,temperature,airconditonertype):
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
    "command": "setAll",
    "parameter": "26,2,1,on",
    "commandType": "command"
    }
    temperature = str(26)
    airconditonertype = "冷房"
    r = requests.post(url, headers=headers, data=json.dumps(params))
    return temperature,airconditonertype

@app.route("/")
def hello_world():
    return "hello world!"#テスト用


@app.route("/light_off")
def light_off():
    operate_switchobot_turnOff(device_id_light, 2)
    return "照明を消しました"

@app.route("/light_on")
def light_on():
    operate_switchobot_turnOn(device_id_light)
    return "照明をつけました"

@app.route("/TV_on")
def TV_on():
    operate_switchobot_turnOn(device_id_tv)
    return "テレビをつけました"

@app.route("TV_off")
def TV_off():
    operate_switchobot_turnOff(device_id_tv, 1)
    return "テレビを消しました"

@app.route("/airconditioner_off")
def airconditioner_off():
    operate_switchobot_turnOff(device_id_airconditioner, 1)
    return "エアコンを消しました"
@app.route("/airconditioner_on")
def airconditioner_on():
    temperature = 0
    airconditonertype = 0
    operate_switchobot_airconditioner_turnOn(device_id_airconditioner,temperature,airconditonertype)
    sentense = "エアコンを" + temperature + "度で" + airconditonertype + "でつけました"
    return sentense
    
  
if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


