import os
from flask import Flask, request
import openai
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json
import requests
from bs4 import BeautifulSoup

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



app = Flask(__name__, static_folder='.', static_url_path='')


@app.route('/')
def index():
    return "this is test"
    
    
# githubの情報をなんとか
@app.route('/userSignup', methods=["POST"])
def signup():
    data = json.loads(request.get_data())

    doc_ref = db.collection("users").document(data['user_id'])
    doc_ref.set({
        "user_name": data["user_name"], 
        "description": data["description"],
        "tech_tags": data["tech_tags"]
    })
    return {"is_success": True}



# 個人イベント作成
@app.route('/createEvent', methods=["POST"])
def create_event():
    data = json.loads(request.get_data())

    doc_ref = db.collection("events").document(data["owner_id"])
    doc = doc_ref.get()

    payload = {data["event_name"]: {
        "date": data["date"],
        "description": data["description"],
        "genre": data["genre"],
        "wait_list": [],
        "member_list": []
    }}

    if doc.exists:
        events = doc.to_dict()
        if data["event_name"] in events:
            return {"is_success": False}
        else:
            doc_ref.update(payload)
            return {"is_success": True}
    else:
        doc_ref.set(payload)
        return {"is_success": True}


# 個人イベント参加申請
@app.route('/joinEvent', methods=['POST'])
def join_event():
    data = json.loads(request.get_data())

    doc_ref = db.collection("events").document(data["owner_id"])
    doc = doc_ref.get()

    waitList = doc.to_dict()[data["event_name"]]["wait_list"]
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


# 個人イベント参加申請者一覧
@app.route('/eventWaitList', methods=["POST"])
def event_wait_list():
    data = json.loads(request.get_data())

    doc_ref = db.collection("events").document(data["owner_id"])
    doc = doc_ref.get()

    waitList = doc.to_dict()[data["event_name"]]["wait_list"]
    return waitList


# 個人イベント参加申込承認
@app.route('/approveEventJoin', methods=['POST'])
def approve_event_join():
    data = json.loads(request.get_data())

    doc_ref = db.collection("events").document(data["owner_id"])
    doc = doc_ref.get()

    waitList = doc.to_dict()[data['event_name']]["wait_list"]
    memberList = doc.to_dict()[data["event_name"]]["member_list"]

    if data["user_id"] in waitList:
        waitList.remove(data["user_id"])
        doc_ref.set({data["event_name"]: {
            "wait_list": waitList
        }}, merge=True)

        memberList.append(data["user_id"])
        doc_ref.set({data["event_name"]: {
            "member_list": memberList
        }}, merge=True)
        return {"is_success": True}
    else:
        return {"is_success": False}


# ハッカソンチーム作成
@app.route('/createTeam', methods=["POST"])
def create_team():
    data = json.loads(request.get_data())

    doc_ref = db.collection("officialEvents").document(data["event_name"])
    doc = doc_ref.get()

    payload = {data["owner_id"]: {
        "team_name": data["team_name"],
        "description": data["description"],
        "needed_tech_tags": data["needed_tech_tags"],
        "wait_list": [],
        "member_list": []
    }}

    if doc.exists:
        owners = doc.to_dict()
        if data["owner_id"] in owners:
            return {"is_success": False}
        else:
            doc_ref.update(payload)
            return {"is_success": True}
    else:
        doc_ref.set(payload)
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


@app.route('/getTagFromTopaz', methods=["GET"])
def get_tag_from_topaz():
    url = "https://topaz.dev/projects"
    response = requests.get(url)

    if response.status_code == 200:
        # HTMLコードをBeautifulSoupオブジェクトに変換する
        soup = BeautifulSoup(response.text, 'html.parser')
        # id="__NEXT_DATA__"を持つ要素を取得する
        next_data = soup.find('script', {'id': '__NEXT_DATA__'})
        data = json.loads(next_data.text)
        tag_list = data["props"]["pageProps"]["technologyTagList"]

        for el in tag_list:
            doc_ref = db.collection("tags").document(el["id"])
            doc = doc_ref.get()

            if not doc.exists:
                doc_ref.set({"type": el["type"],
                            "icon_path": el["iconPath"]})
        # for el in tag_list:
        #     doc_ref = db.collection("tags").document(el["type"])
        #     doc_ref.set({el["id"]: {
        #                  "icon_path": el["iconPath"]}
        #                  }, merge=True)
        return {"is_success": True}
    else:
        return {"is_success": False}


# 全てのタグを取得
@app.route('/getAllTags', methods=["GET"])
def get_all_tags():
    collection_ref = db.collection("tags")
    docs = collection_ref.get()

    tags = {}
    for doc in docs:
        tags[doc.id] = {"type": doc.to_dict()["type"],
                        "icon_path": doc.to_dict()["icon_path"]}
    return tags


# 必要なタグだけを取得
@app.route('/getMatchTags', methods=['POST'])
def get_match_tags():
    data = json.loads(request.get_data())

    collection_ref = db.collection("tags")
    docs = collection_ref.get()

    tags = {}
    for tag_needed in data["tags"]:
        doc_ref = collection_ref.document(tag_needed)
        doc = doc_ref.get().to_dict()
        tags[tag_needed] = {"type": doc["type"],
                            "icon_path": doc["icon_path"]}
    return tags


# プロフィールを取得
@app.route('/getProfile', methods=["POST"])
def get_profile():
    data = json.loads(request.get_data())

    doc_ref = db.collection("users").document(data["user_id"])
    doc = doc_ref.get().to_dict()

    return doc


# ハッカソンのチームをchatGPTでソート Aさんの得意な技術を列挙し、全ての技術タグから相性の良いタグをソートしてもらう
@app.route('/sortTeamList', methods=["POST"])
def sort_team_list():
    data = json.loads(request.get_data())

    doc_ref = db.collection("users").document(data["user_id"])
    doc = doc_ref.get().to_dict()

    tech_tags = doc["tech_tags"]

    all_tags = list(get_all_tags().keys())

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[    
            {"role": "user", "content": f"Aさんは{tech_tags}が得意です。バックエンドやフロントエンド、インフラなどを考慮し、Aさんとの相性が良い順に技術に関する配列{all_tags}を並び替えてください。並び替えた配列に{tech_tags}を含まないでください。"},
        ],
    )
    print(response.choices[0]["message"]["content"].strip())

    return response


app.run(port=5003, debug=True)
