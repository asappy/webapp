from flask import Flask
import os
import requests
import json
import time
import base64
import hmac
import hashlib

app = Flask(__name__)

SWITCHBOT_AUTH_KEY = '753fc75e5a8094fd7fdd3d1ddf23817d7c72e5a16ce0a4c33f34b22aa470709db7d933946ccf72dfff08e10b60ed0545'
SWITCHBOT_SECRET = 'b2c26a06812dbb265e4d01f51a1f16fb'

# auth_key = os.environ[SWITCHBOT_AUTH_KEY] # copy and paste from the SwitchBot app V6.14 or later
# secret = os.environ[SWITCHBOT_SECRET] # copy and paste from the SwitchBot app V6.14 or later
auth_key = SWITCHBOT_AUTH_KEY
secret = SWITCHBOT_SECRET

device_id_light = "02-202207132247-89473231"
device_id_airconditioner = "02-202207132236-15163498"
device_id_tv = "02-202207132329-83831759"

url = "https://api.switch-bot.com/v1.0/devices"

def generate_sign(token: str, secret: str, nonce: str) -> tuple[str, str]:
    #SWITCH BOT APIの認証キーを生成する

    t = int(round(time.time() * 1000))
    string_to_sign = "{}{}{}".format(token, t, nonce)
    string_to_sign_b = bytes(string_to_sign, "utf-8")
    secret_b = bytes(secret, "utf-8")
    sign = base64.b64encode(
        hmac.new(secret_b, msg=string_to_sign_b, digestmod=hashlib.sha256).digest()
    )

    return (str(t), str(sign, "utf-8"))

headers = {
    'Authorization': auth_key,
    'Content-Type': 'application/json; charset=utf8'
}
r = requests.get(url, headers=headers)
print("status=", r.status_code)

json_data = r.json()
s = json.dumps(json_data, indent=2) #jsonデータを整形
print(s)
