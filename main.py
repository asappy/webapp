from flask import Flask, render_template, request, redirect, flash, session, url_for
import os
import requests
import json
import time
import base64
import hmac
import hashlib

app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24)
app.config['USERNAME'] = 'user'
app.config['PASSWORD'] = 'pass'

app.config['USERNAME'] = os.environ["WEB_USERNAME"]
app.config['PASSWORD'] = os.environ["WEB_PASSWORD"]


# SWITCHBOT_AUTH_KEY = '753fc75e5a8094fd7fdd3d1ddf23817d7c72e5a16ce0a4c33f34b22aa470709db7d933946ccf72dfff08e10b60ed0545'
# SWITCHBOT_SECRET = 'b2c26a06812dbb265e4d01f51a1f16fb'

# auth_key = SWITCHBOT_AUTH_KEY
# secret = SWITCHBOT_SECRET

auth_key = os.environ["SWITCHBOT_AUTH_KEY"] # copy and paste from the SwitchBot app V6.14 or later
secret = os.environ["SWITCHBOT_SECRET"] # copy and paste from the SwitchBot app V6.14 or later


device_id_light = "02-202207132247-89473231"
device_id_airconditioner = "02-202207132236-15163498"
device_id_tv = "02-202207132329-83831759"

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

def get_devicelist():
    url = "https://api.switch-bot.com/v1.0/devices"
    headers = {
        'Authorization': auth_key,
        'Content-Type': 'application/json; charset=utf8'
    }
    r = requests.get(url, headers=headers)
    print("status=", r.status_code)

    json_data = r.json()
    s = json.dumps(json_data, indent=2) #jsonデータを整形
    print(s)


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

def operate_switchobot_airconditioner_turnOn(ID, temperature, airconditonertype):
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


#app = Flask(__name__, static_folder='./static')

@app.route("/")
def welcome():
    if "flag" in session and session["flag"]:
        return render_template('index.html', username=session["username"])
    return redirect('/login')

@app.route("/login", methods=["GET"])
def login():
    if "flag" in session and session["flag"]:
        return redirect("/index")
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login_post():
    username = request.form["username"]
    password = request.form["password"]
    print("aa")
    if username != app.config["USERNAME"]:
        flash("ユーザ名が異なります")
    elif password != app.config["PASSWORD"]:
        flash("パスワードが異なります")
    else:

        session["flag"] = True
        session["username"] = username
    if session["flag"]:
        return render_template("index.html", username=session["username"])
    else:
        return redirect("/login")

# ログイン処理
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         # 画面で入力された情報を取得
#         username = request.form['username']
#         password = request.form['password']

#         # ログイン可否を判定
#         if app.config["USERNAME"] and app.config["PASSWORD"] == password:
#             session['username'] = username

#             # ログイン成功でdashbord.htmlを返す
#             return redirect(url_for('index'))
#         else:
#             return render_template('login.html', error='Invalid credentials')

#     # GETの場合はログイン画面へ戻す
#     return render_template('login.html')


@app.route("/index")
def index():
    if "flag" in session and session["flag"]:
        return render_template("index.html", username=session["username"])
    return redirect("/login")

@app.route('/dashboard')
def dashboard():
    # ログインしている場合はdashbord.htmlへ
    if 'username' in session:
        return render_template('dashbord.html')
    else:
        return redirect(url_for('login'))


@app.route("/light_off")
def light_off():
    if "flag" in session and session["flag"]:
        operate_switchobot_turnOff(device_id_light, 2)
        return render_template("light_off.html", username=session["username"])
    return redirect("/login")

@app.route("/light_on")
def light_on():
    if "flag" in session and session["flag"]:
        operate_switchobot_turnOn(device_id_light)
        #get_devicelist()
        return render_template("light_on.html", username=session["username"])
    return redirect("/login")


@app.route("/TV_on")
def TV_on():
    if "flag" in session and session["flag"]:
        operate_switchobot_turnOn(device_id_tv)
        return render_template("tv_on.html", username=session["username"])
    return redirect("/login")

@app.route("/TV_off")
def TV_off():
    if "flag" in session and session["flag"]:
        operate_switchobot_turnOff(device_id_tv, 1)
        return render_template("tv_off.html", username=session["username"])
    return redirect("/login")

@app.route("/air_off")
def airconditioner_off():
    if "flag" in session and session["flag"]:
        operate_switchobot_turnOff(device_id_airconditioner, 1)
        return render_template("air_off.html", username=session["username"])
    return redirect("/login")

@app.route("/air_on")
def airconditioner_on():
    if "flag" in session and session["flag"]:
        temperature = str(0)
        airconditonertype = str(0)
        operate_switchobot_airconditioner_turnOn(device_id_airconditioner,temperature,airconditonertype)
        sentense = "エアコンを" + temperature + "度で" + airconditonertype + "でつけました"
        return render_template("air_on.html", username=session["username"])
    return redirect("/login")

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# ローカル環境
# if __name__ == "__main__":
#     port = int(os.getenv("PORT", 8000))
#     app.run(host="0.0.0.0", port=port, debug=True)
# 本番用
if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT",8000))
    app.run(host="0.0.0.0", port=port)

# 参考サイト
# https://hirahira.blog/pyhton-flask-login/
# https://www.learning-nao.com/?p=4306
