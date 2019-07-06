# import common 
import sys
sys.path.append('../common/')
from functions import get_videos, get_view_data, create_chart, do_predict

import pandas as pd
from flask import Flask, request, render_template, jsonify, redirect, url_for
from bokeh.embed import components
from pymongo import MongoClient

connection = MongoClient(port=47017)
db = connection['youtube_scrap']

app = Flask(__name__, static_url_path="")

@app.route('/')
def index():
    """Return the main page."""
    videos = get_videos(db, count=3)
    stats= {
        'videos': 123,
        'increments': 4000,
    }
    return render_template('index.html', 
                            counts=len(videos),
                            stats=stats, 
                            videos=videos)

@app.route('/about')
def about():
    """Return the about page."""
    return render_template('about.html')

@app.route('/detail', methods=['GET'])
def detail():
    """Return video detail page."""    
    video_id = request.args.get('video_id')
    data = get_view_data(db, video_id)
    hover=None
    future = do_predict(pd.DataFrame(data))
    plot = create_chart(future, "View Counts", hover)
    script, div = components(plot)

    return render_template('detail.html', counts=len(data), 
                            data=data, video=None, 
                            the_script=script, the_div=div)
