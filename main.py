import os
from flask import Flask, request
import openai
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json
import requests

# firebaseのapiの設定
cred = credentials.Certificate(
    "./jinbee-cup-firebase-adminsdk-y7xm5-80b53cb07f.json")

firebase_admin.initialize_app(cred)
db = firestore.client()

# chatgptのAPIキーの設定
openai.api_key = os.environ["OPENAI_API_KEY"]


# response = openai.ChatCompletion.create(
#     model="gpt-3.5-turbo",
#     messages=[
#         {"role": "user", "content": "大谷翔平について教えて"},
#     ],
# )
# print(response.choices[0]["message"]["content"].strip())

def send_to_database():
    doc_ref = db.collection("test").document("test_id")
    # firestore.ArrayUnion　<=おまじない
    doc_ref.set({'key': 'value'})


# 使用言語の取得
# username = "shotaro-ada"
# url = f"https://api.github.com/users/{username}/repos"
# response = requests.get(url)

# languages = []
# for repo in response.json():
#     language = repo["language"]
#     if language is not None and language not in languages:
#         languages.append(language)

# print(f"{username}が使用している言語: {', '.join(languages)}")


app = Flask(__name__, static_folder='.', static_url_path='')


@app.route('/')
def index():
    return "this is test"


# 個人プロダクトイベント作成
@app.route('/createEvent', methods=["POST"])
def create_event():
    data = json.loads(request.get_data())

    doc_ref = db.collection("events").document(data["owner_id"])
    doc = doc_ref.get()

    events = doc.to_dict()

    if data["event_name"] in events:
        return {"is_success": False}
    else:
        doc_ref.update({data["event_name"]: {
            "date": data["date"],
            "description": data["description"],
            "genre": data["genre"],
            "wait_list": [],
            "member_list": []
        }})
        return {"is_success": True}


# 個人プロダクト参加申請
@app.route('/joinEvent', methods=['POST'])
def join_event():
    data = json.loads(request.get_data())

    doc_ref = db.collection("events").document(data["owner_id"])
    doc = doc_ref.get()

    waitList = doc.to_dict()[data["evnet_name"]]["wait_list"]
    memberList = doc.to_dict()[data["event_name"]]["member_list"]

    if data["user_id"] in memberList:
        return {"is_success": False}
    elif data["user_id"] in waitList:
        return {"is_success": False}
    else:
        waitList.append(data["user_id"])
        doc_ref.set({data["event_name"]: {
            "wait_list": waitList
        }}, merge=True)
        return {"is_success": True}


# ハッカソンチーム作成
@app.route('/createTeam', methods=["POST"])
def create_team():
    data = json.loads(request.get_data())

    doc_ref = db.collection("officialEvents").document(data["event_name"])
    doc = doc_ref.get()

    owners = doc.to_dict()

    if data["owner_id"] in owners:
        return {"is_success": False}
    else:
        doc_ref.update({data["owner_id"]: {
            "team_name": data["team_name"],
            "description": data["description"],
            "needed_tech_tags": data["needed_tech_tags"],
            "wait_list": [],
            "member_list": []
        }})
        return {"is_success": True}


# ハッカソんチーム参加
@app.route('/joinTeam', methods=["POST"])
def join_team():
    data = json.loads(request.get_data())

    doc_ref = db.collection("officialEvents").document(data["event_name"])
    doc = doc_ref.get()

    waitList = doc.to_dict()[data["owner_id"]]["wait_list"]
    memberList = doc.to_dict()[data["owner_id"]]["member_list"]

    if data["user_id"] in memberList:
        return {"is_success": False}
    elif data["user_id"] in waitList:
        return {"is_success": False}
    else:
        waitList.append(data["user_id"])
        doc_ref.set({data["owner_id"]: {
            "wait_list": waitList
        }}, merge=True)
        return {"is_success": True}


# ハッカソンチーム参加申請者取得
@app.route('/teamWaitList', methods=["POST"])
def team_wait_list():
    data = json.loads(request.get_data())

    doc_ref = db.collection("officialEvents").document(data["event_name"])
    doc = doc_ref.get()

    waitList = doc.to_dict()[data["owner_id"]]["wait_list"]
    return waitList


# ハッカソン参加申込承認
@app.route('/approveTeamJoin', methods=['POST'])
def approve_team_join():
    data = json.loads(request.get_data())

    doc_ref = db.collection("officialEvents").document(data["event_name"])
    doc = doc_ref.get()

    waitList = doc.to_dict()[data['owner_id']]["wait_list"]
    memberList = doc.to_dict()[data["owner_id"]]["member_list"]

    if data["user_id"] in waitList:
        waitList.remove(data["user_id"])
        doc_ref.set({data["owner_id"]: {
            "wait_list": waitList
        }}, merge=True)

        memberList.append(data["user_id"])
        doc_ref.set({data["owner_id"]: {
            "member_list": memberList
        }}, merge=True)
        return {"is_success": True}
    else:
        return {"is_success": False}

        
app.run(port=5007, debug=True)
