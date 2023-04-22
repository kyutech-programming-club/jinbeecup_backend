import os
from flask import Flask, request
import openai
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json
import requests

#firebaseのapiの設定
cred = credentials.Certificate("./jinbee-cup-firebase-adminsdk-y7xm5-80b53cb07f.json")

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


#使用言語の取得
username = "shotaro-ada"
url = f"https://api.github.com/users/{username}/repos"
response = requests.get(url)

languages = []
for repo in response.json():
    language = repo["language"]
    if language is not None and language not in languages:
        languages.append(language)

print(f"{username}が使用している言語: {', '.join(languages)}")



app = Flask(__name__, static_folder='.', static_url_path='')

@app.route('/')
def index():
    return "this is test"

@app.route('/createEvent', methods=["POST"])
def create_event():
    data = json.loads(request.get_data())['data']

    doc_ref = db.collection("events").document(data["user_id"])
    doc_ref.update({data["event_name"]: {
        "date": data["date"],
        "description": data["description"],
        "tags": data["tags"]
    }})
    return data["user_id"]


app.run(port=5002, debug=True)
