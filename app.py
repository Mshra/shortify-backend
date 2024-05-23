from logging import debug
from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv, main
import os

load_dotenv()

app = Flask(__name__)
client = MongoClient(os.getenv('URI'))
db = client['shortener']
CORS(app)

def generate_short_url(length=6):
    import string, random
    characters = string.ascii_letters + string.digits
    short_url = ''.join(random.choice(characters) for _ in range(length))
    return short_url

@app.route('/')
def hello():
    return 'hello'

@app.route('/shorten', methods=['POST'])
def shorten():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No URL given"}), 400

    original_url = data['original_url']
    existing_url = db.users.find_one({ "original_url": original_url})

    if existing_url:
        shorten_url = existing_url['shorten_url']
    else:
        shorten_url = "https://sfy.vercel.app/" + str(generate_short_url())
        db.users.insert_one({ 'original_url': original_url, 'shorten_url': shorten_url})

    return jsonify({ 'shorten_url': shorten_url}), 201

@app.route('/<string:shorten_url>')
def redirect(shorten_url):
    url = "https://sfy.vercel.app/" + shorten_url

    redirect_url = db.users.find_one({ "shorten_url": url})

    if redirect_url:
        return redirect(redirect_url["original_url"])
    else:
        return jsonify({ "url not found", url})

@app.route('/<string:shorten_url>/delete', methods=['DELETE'])
def delete(shorten_url):
    s_url = "https://sfy.vercel.app/" + shorten_url
    try:
        result = db.users.delete_one({ "shorten_url": s_url})
        if result.deleted_count == 1:
            return jsonify({"message": "User deleted successfully"}), 200
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
