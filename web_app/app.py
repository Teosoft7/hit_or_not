import pandas as pd
from flask import Flask, request, render_template, jsonify, redirect, url_for
from functions import get_last4_videos, get_view_data, create_chart
from bokeh.embed import components
from pymongo import MongoClient

from collections import ChainMap

# import pickle
# with open('spam_model.pkl', 'rb') as f:
#     model = pickle.load(f)

connection = MongoClient()
db = connection['youtube_scrap']

app = Flask(__name__, static_url_path="")

@app.route('/')
def index():
    """Return the main page."""
    last_video = get_last4_videos(db)
    return render_template('index.html', last_video=last_video)

@app.route('/about')
def about():
    """Return the about page."""
    return render_template('about.html')

@app.route('/detail')
def detail(video_id=None):
    """Return video detail page."""
    data = get_view_data(db, 'nM0xDI5R50E')
    hover=None
    
    plot = create_chart(data, "View Counts", hover)
    script, div = components(plot)

    return render_template('detail.html', counts=len(data), 
                            data=data, video=None, 
                            the_script=script, the_div=div)

# @app.route('/predict', methods=['GET', 'POST'])
# def predict():
#     """Return a random prediction."""
#     data = request.json
#     prediction = model.predict_proba([data['user_input']])
#     return jsonify({'probability': prediction[0][1]})

