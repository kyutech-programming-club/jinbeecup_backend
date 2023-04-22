import os
from flask import Flask
import openai
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

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

send_to_database()

# app = Flask(__name__, static_folder='.', static_url_path='')
# @app.route('/')
# def index():
#     return "this is test"

# app.run(port=8000, debug=True)