import pandas as pd
import numpy as np
import time

from matplotlib import pyplot as plt
from matplotlib import dates as mdates
from datetime import datetime, timedelta
from fbprophet import Prophet

from pymongo import MongoClient, DESCENDING

from bokeh.plotting import figure
from bokeh.models import NumeralTickFormatter

# Used for index.html page
def get_videos(db, count=3):
    """Return the random selected video from the db"""
    video_coll = db['video_detail']
    view_coll = db['view_count']

    cursor = video_coll.find({})
    videos = [video for video in cursor]

    idx = np.arange(len(videos))
    selected = np.random.choice(idx, count, replace=False)
    
    selected_video = []
    for idx in selected:
        selected_video.append(videos[idx])

    result = []
    for video in selected_video:
        filter = {'video_id': video['video_id']}
        view_cursor = view_coll.find(filter).sort('timestamp', 
                                                  DESCENDING).limit(1)
        views = view_cursor.next()

        if views['view_count'] > 1_000_000_000:
            views['view_count'] = f'{views["view_count"] / 1_000_000_000:.1f}B'
        elif views['view_count'] > 1_000_000:
            views['view_count'] = f'{views["view_count"] / 1_000_000:.1f}M'
        elif views['view_count'] > 1_000:
            views['view_count'] = f'{views["view_count"] / 1_000:.1f}K'

        record = video
        record.update(views)
        result.append(record)

    # print(result)
    return result

def get_collection_count(db, collection_name):
    """Return total documents count of collection"""
    coll = db[collection_name]
    return coll.count_documents({})

def get_increments(db, period=4):
    """Return sum of view_count for last period(default=12) hours"""
    ago = datetime.now() - timedelta(hours=period)
    coll = db['view_count']
    cur = coll.find({'timestamp': {"$gt": ago}})
    return sum([row['view_count'] for row in cur])

def get_count_string(value):
    """Return string value with Billion/Million/Kilo"""
    if value > 1_000_000_000:
        return "{:,.1f} B".format(value / 1_000_000_000)
    elif value > 1_000_000:
        return "{:,.1f} M".format(value / 1_000_000)
    elif value > 1_000:
        return "{:,.1f} K".format(value / 1_000)
    
    return "{:,.1f}".format(value)

def get_view_data(db, video_id):
    """Return view_count collection for video_id"""
    view_count_coll = db['view_count']
    filter = {'video_id': video_id}
    cursor = view_count_coll.find(filter).sort('timestamp', DESCENDING)

    return [record for record in cursor]

def do_predict(data, periods=3):
    """Return predicted view_count for period days """
    # initialize Prophet model
    m = Prophet()

    # prepare dataframe for Prophet
    est_df = data[['timestamp', 'view_count']]
    est_df.columns = ['ds', 'y']

    # fit to model
    m.fit(est_df)
    future = m.make_future_dataframe(periods=periods)
    forecast = m.predict(future)
    
    return forecast

def create_chart(data, title, hover_tool=None,
                 width=1024, height=480):
    """Create a line chart with data"""

    counts = data['yhat']
    times = data['ds']
    predict_times = times.tail(4)

    label=''
    divider = 1
    if counts.min() > 1_000_000:
        divider = 1_000_000
        label = ' (M)'
    elif counts.min() > 1_000:
        divider = 1_000
        label = ' (K)'

    counts = data['yhat'] / divider
    predict_counts = data['yhat'].tail(4) / divider
    predict_upper = data['yhat_upper'].tail(4) / divider
    predict_lower = data['yhat_lower'].tail(4) / divider

    p = figure(plot_width=width, 
               plot_height=height,
               x_axis_type="datetime",
               sizing_mode='scale_width')

    p.line(times, counts, 
           line_width=2, color='navy', legend='view counts')

    p.line(predict_times, predict_counts, 
           line_width=3, color='red', line_dash='dashed', 
           legend='prediction')

    p.line(predict_times, predict_upper, 
           line_width=2, color='red', line_dash='dotted', 
           legend='upper bound')

    p.line(predict_times, predict_lower, 
           line_width=2, color='red', line_dash='dotted', 
           legend='lower bound')

    p.title.text = title
    p.legend.location = "top_left"
    p.grid.grid_line_alpha = 0
    p.xaxis.axis_label = 'Date'
    p.yaxis.axis_label = 'Views' + label
    p.background_fill_color = "beige"
    p.background_fill_alpha = 0.5
    p.yaxis[0].formatter = NumeralTickFormatter(format="0.000")

    return p

def get_all_collection(coll, filters=None):
    """Returns the list of objects in mongodb collection"""
    cursor = coll.find({})
    results = [obj for obj in cursor]
    return results

def draw_barchart(x, 
                  y,
                  xlabel='title',
                  ylabel='count',
                  title='Top 5', 
                  figsize=(8, 6)):
    """Draw bar chart for top5 video"""
    
    fig, ax = plt.subplots(figsize=figsize)
    fig.suptitle(title)

    ax.bar(x, y)

    ax.set_xlabel(xlabel, fontsize=14)
    ax.set_ylabel(ylabel, fontsize=14)

    labels = [title[:10] + '...' for title in x]
    plt.xticks(x, labels)

    plt.show()

def get_view_counts(db, video_id):
    """Return all scrapped view count for video_id"""
    view_count_coll = db['view_count']
    cur = view_count_coll.find({'video_id': video_id}).sort('timestamp')
    
    view_counts = [record for record in cur]
    return pd.DataFrame(view_counts)

def draw_count_chart(data, fields=['view_count'], title='Count by Time', figsize=(12, 6)):
    """Draw a chart with data(timestamp, counts)"""
    fig, ax = plt.subplots(figsize=figsize)
    fig.suptitle(title)

    divider = 1
    div_label = ''

    for field in fields:
        divider = 1_000 if data[field].max() > 90_000 else divider
        div_label = ' (K)' if divider == 1_000 else div_label

        divider = 1_000_000 if data[field].max() > 90_000_000 else divider
        div_label = ' (M)' if divider == 1_000_000 else div_label

        ax.plot(data['timestamp'], 
                data[field] / divider, 
                '-',
                label=field)

    hours = mdates.HourLocator(interval = 4)
    h_fmt = mdates.DateFormatter('%m%d-%H:%M')

    ax.xaxis.set_major_locator(hours)
    ax.xaxis.set_major_formatter(h_fmt)

    ax.set_xlabel('Time')
    ax.set_ylabel('Count' + div_label)
    fig.autofmt_xdate()
    plt.legend()
    plt.show()

