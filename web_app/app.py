
import sys
sys.path.append('../common/')

# my functions
from functions import (get_videos, 
                        get_view_data, 
                        create_chart, 
                        do_predict,
                        get_count_string,
                        get_sum_view_count,
                        get_collection_count,
                        get_hot_video,
                        get_most_watched_video,)

# import common libraries
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
    # get random 3 videos for display
    videos = get_videos(db, count=3)

    # get total view counts and increments for last 4 hours
    total_view, increments = get_sum_view_count(db)
    stats= {
        'videos': get_collection_count(db, 'video_detail'),
        'increments': get_count_string(increments),
        'total_view': get_count_string(total_view)
    }

    # return with template
    return render_template('index.html', 
                            counts=len(videos),
                            stats=stats, 
                            videos=videos)

@app.route('/hottrend')
def hot_trend():
    """Return hot trend page."""
    # Need to add data set for hot trend
    # Hot : top 10 most increments views for last 4 hours
    count = 10
    videos = get_hot_video(db, count=count)
    
    # apply format for large numbers
    for video in videos:
        video['view_count'] = get_count_string(video['view_count'])
        video['increment'] = get_count_string(video['increment'])

    return render_template('hot_trend.html', videos=videos, count=count)

@app.route('/mostwatched')
def most_watched():
    """Return most watched page."""
    # Need to add data set for most_watched
    # Most watched : top 10 most watched video
    count = 10
    videos = get_most_watched_video(db, count=count)
    
    # apply format for large numbers
    for video in videos:
        video['view_count'] = get_count_string(video['view_count'])

    return render_template('most_watched.html', videos=videos, count=count)

@app.route('/newreleased')
def new_released():
    """Return new released page."""
    # Need to add data set for new released
    # new_released : top 10 most recently released video
    return render_template('new_released.html')

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
