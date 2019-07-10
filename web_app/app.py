
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
                       get_most_watched_video,
                       get_most_recent_video,
                       get_video_detail,
                       get_daily_view_count,
                       create_bar_chart,
                       get_increment_view,)

# import common libraries
import pandas as pd
from flask import Flask, request, render_template, url_for
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
                            count=len(videos),
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
    # new_released : top 6 most recently released video
    count = 6
    videos = get_most_recent_video(db, count=count)

    return render_template('new_released.html', videos=videos, count=count)

@app.route('/about')
def about():
    """Return the about page."""
    return render_template('about.html')

@app.route('/detail', methods=['GET'])
def detail():
    """Return video detail page.""" 

    # get video id   
    video_id = request.args.get('video_id')

    # get detail info about video
    video = get_video_detail(db, video_id)
    video['view_count'] = get_count_string(video['view_count'])
    video['like_count'] = get_count_string(video['like_count'])
    video['comment_count'] = get_count_string(video['comment_count'])

    # get increments and update to video
    increment = get_increment_view(db, video_id)
    video['increment'] = get_count_string(increment['increment'])
    
    # perform predict with fbProPhet
    data = get_view_data(db, video_id)
    future = do_predict(pd.DataFrame(data))
    video['prediction'] = get_count_string(future['yhat'].tail(1).values[0])

    # Draw a chart with Bokeh
    plot = create_chart(future, 
                        "View Counts", 
                        video_id)
                        
    script, div = components(plot)

    return render_template('detail.html', 
                            video=video, 
                            the_script=script, 
                            the_div=div)
