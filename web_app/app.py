from flask import Flask, request, render_template, jsonify, redirect, url_for
from pymongo import MongoClient

import pickle

# with open('spam_model.pkl', 'rb') as f:
#     model = pickle.load(f)

connection = MongoClient(port=47017)
db = connection['youtube_scrap']

app = Flask(__name__, static_url_path="")

def get_last3_videos():
    video_coll = db['video_detail']
    cursor = video_coll.find({}).limit(3)
    return [record for record in cursor]

@app.route('/')
def index():
    """Return the main page."""
    last3_video = get_last3_videos()
    return render_template('index.html', last3_video=last3_video)

@app.route('/about')
def about():
    """Return the about page."""
    return render_template('about.html')

@app.route('/detail')
def detail():
    """Return video detail page."""
    return render_template('detail.html')

# @app.route('/predict', methods=['GET', 'POST'])
# def predict():
#     """Return a random prediction."""
#     data = request.json
#     prediction = model.predict_proba([data['user_input']])
#     return jsonify({'probability': prediction[0][1]})

