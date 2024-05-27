from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
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
    return 'URL Shortener'

@app.route('/shorten', methods=['POST'])
def shorten():
    data = request.get_json()

    original_url = data['original_url']
    existing_url = db.users.find_one({ "original_url": original_url})

    if existing_url:
        shorten_url = existing_url['shorten_url']
    else:
        shorten_url = f"{os.getenv('API_URI')}" + str(generate_short_url())
        db.users.insert_one({ 'original_url': original_url, 'shorten_url': shorten_url})

    return jsonify({ 'shorten_url': shorten_url}), 201

@app.route('/<string:shorten_url>')
def redirect_url(shorten_url):
    url = f"{os.getenv('API_URI')}" + shorten_url

    new_url = db.users.find_one({ "shorten_url": url})

    if new_url:
        return redirect(new_url["original_url"]["url"])
    else:
        return "You are lost!The URL you entered does not exist.", 404

@app.route('/<string:shorten_url>/delete', methods=['DELETE'])
def delete(shorten_url):
    s_url = f"{os.getenv('API_URI')}" + shorten_url
    try:
        result = db.users.delete_one({ "shorten_url": s_url})
        if result.deleted_count == 1:
            return jsonify({"message": "User deleted successfully"}), 200
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
