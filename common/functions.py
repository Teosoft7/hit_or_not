import pandas as pd
import numpy as np
import time

from matplotlib import pyplot as plt
from matplotlib import dates as mdates
from datetime import datetime, timedelta
from fbprophet import Prophet

from pymongo import MongoClient, DESCENDING

from bokeh.plotting import figure
from bokeh.models import (CustomJS,
                          Div, 
                          Row, 
                          NumeralTickFormatter, 
                          DatetimeTickFormatter)

# Used for index.html page
def get_videos(db, count=3):
    """Return the random selected video from the db"""
    video_coll = db['video']
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
        # apply string format
        views['view_count'] = get_count_string(views['view_count'])

        record = video
        record.update(views)
        result.append(record)

    # print(result)
    return result

def get_video_detail(db, video_id):
    """Return video detail & current view, comment, like count
       for video_id"""

    # get video detail first
    coll = db['video']
    cur = coll.find({'video_id': video_id})
    video = cur.next()
    
    coll = db['view_count']
    cur = coll.aggregate([
        {'$match': {'video_id': video_id}},
        {'$group' : {'_id':'$video_id', 
                    'view_count':{'$max':'$view_count'}, 
                    'like_count':{'$max':'$like_count'},
                    'comment_count':{'$max':'$comment_count'},
                    }
        }
    ])
    # update video with views
    video.update(cur.next())
    
    return video

def get_collection_count(db, collection_name):
    """Return total documents count of collection"""
    coll = db[collection_name]
    return coll.count_documents({})

def get_sum_view_count(db, period=4):
    """Return sum of max(view_counts) and sum of view counts for 
    last period(default=4) hours"""
    ago = datetime.now() - timedelta(hours=period)
    coll = db['view_count']
    min_cur = coll.aggregate([
        {'$match': {'timestamp': {"$gt": ago}}},
        {'$group' : {'_id':'$video_id', 
                 'view_count':{'$min':'$view_count'} 
                }
        }
    ])
    max_cur = coll.aggregate([
        {'$match': {'timestamp': {"$gt": ago}}},
        {'$group' : {'_id':'$video_id', 
                 'view_count':{'$max':'$view_count'} 
                }
        }
    ])   

    new_value = sum([row['view_count'] for row in max_cur])
    old_value = sum([row['view_count'] for row in min_cur])
    return new_value, new_value - old_value

def get_count_string(value):
    """Return string value with Billion/Million/Kilo"""
    if value > 1_000_000_000:
        return "{:,.2f} B".format(value / 1_000_000_000)
    elif value > 1_000_000:
        return "{:,.2f} M".format(value / 1_000_000)
    elif value > 1_000:
        return "{:,.2f} K".format(value / 1_000)
    
    return "{:,.0f}".format(value)

def get_view_data(db, video_id):
    """Return view_count collection for video_id"""
    view_count_coll = db['view_count']
    filter = {'video_id': video_id}
    cursor = view_count_coll.find(filter).sort('timestamp', DESCENDING)

    return [record for record in cursor]

def get_increment_view(db, video_id, hours=4):
    """Return increment of view count in last n(4) hours"""
    ago = datetime.now() - timedelta(hours=hours)
    view_count_coll = db['view_count']
    cur = view_count_coll.aggregate([
        {'$match': {'timestamp': {"$gt": ago},
                    'video_id': video_id}
        },
        {'$group': {'_id':'$video_id', 
                    'prev_count': {'$min':'$view_count'} ,
                    'view_count': {'$max':'$view_count'}} },
        {'$addFields': {'increment': 
                        {'$subtract': 
                        ['$view_count', '$prev_count']}}},
        { "$sort": { "increment": -1 } }
    ])
    result = [row for row in cur]
    return result[0]

def get_hot_video(db, count=10, hours=4):
    """Return top 10 most view increased video for last n(=4) hours"""
    # set 4 hours ago
    ago = datetime.now() - timedelta(hours=hours)
    view_count_coll = db['view_count']
    cur = view_count_coll.aggregate([
        {'$match': {'timestamp': {"$gt": ago}}},
        {'$group': {'_id':'$video_id', 
                    'prev_count': {'$min':'$view_count'} ,
                    'view_count': {'$max':'$view_count'}} },
        {'$addFields': {'increment': 
                        {'$subtract': 
                        ['$view_count', '$prev_count']}}},
        { "$sort": { "increment": -1 } }
    ])

    # save query result to list
    video_views = [row for row in cur]
    
    # loop through count elements
    # get video detail and set view_count & increment
    video_coll = db['video']
    for row in video_views[:count]:
        video_id = row['_id']
        cur = video_coll.find({'video_id': video_id})
        video = cur.next()
        row.update(video)

    # return video list
    return video_views[:count]

def get_most_watched_video(db, count=10):
    """Return top 10 most view increased video for last n(=4) hours"""

    # get max view_count among the view counts group by video_id
    view_count_coll = db['view_count']
    current_cur = view_count_coll.aggregate([
        {'$group' : {'_id':'$video_id', 
                    'view_count':{'$max':'$view_count'} 
                    }
        },
        { "$sort": { "view_count": -1 } }
    ])

    # save query result to list
    video_views = [row for row in current_cur]
    
    # loop through count elements
    # get video detail and set view_count & increment
    video_coll = db['video']
    for row in video_views[:count]:
        video_id = row['_id']
        cur = video_coll.find({'video_id': video_id})
        video = cur.next()
        row.update(video)

    # return video list
    return video_views[:count]

def get_most_recent_video(db, count=10):
    """Return top 10 most view increased video for last n(=4) hours"""
    # get video detail and set view_count & increment
    video_coll = db['video']
    cur = video_coll.find({}).sort('published_date', -1).limit(count)
    
    # get view_counts
    view_coll = db['view_count']
    videos = [video for video in cur]
    for video in videos:
        filter = {'video_id': video['video_id']}
        view_cursor = view_coll.find(filter).sort('timestamp', 
                                                  DESCENDING).limit(1)
        views = view_cursor.next()
        video.update(views)
        # apply string format
        video['view_count'] = get_count_string(video['view_count'])

    # return video list
    return videos

def do_predict(data, periods=3):
    """Return predicted view_count for period(default:3) days """
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

def get_daily_view_count(db, video_id, days=7):
    """Return daily view count for video_id"""
    # get max(view_count) group by video_id and date
    coll = db['view_count']
    cur = coll.aggregate([
        {'$match': {'video_id': video_id}},
        { '$group': {
                '_id': {'video_id': '$video_id',
                        'year' : { '$year' : '$timestamp' },     
                        'month' : { '$month' : '$timestamp' },     
                        'day' : { '$dayOfMonth' : '$timestamp' }},                        
                'view_count': {'$max': '$view_count'}
                }},
        { '$sort': {'_id.video_id': 1,
                    '_id.year':-1, 
                    '_id.month': -1, 
                    '_id.day': -1}}
    ])
    view_by_day = [{'video_id': row['_id']['video_id'],
                    'date': datetime(row['_id']['year'], 
                            row['_id']['month'], 
                            row['_id']['day']),
                    'view_count': row['view_count']}
                    for row in cur]

    return view_by_day[:days]

def create_chart(data, title, video_id,
                 width=800, height=480):
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

    # add background image to chart
    # url = f'http://img.youtube.com/vi/{video_id}/mqdefault.jpg'
    # html = '<div style="position: absolute; left:-1280px; top:0px">'
    # html += '<img src='  
    # html += url + f' style="width:100%; height:100%;'
    # html += 'opacity: 0.3"></div>'
    # d1 = Div(text = html)

    p.title.text = title
    p.legend.location = "top_left"
    p.grid.grid_line_alpha = 0
    p.xaxis.axis_label = 'Date'
    p.yaxis.axis_label = 'Views' + label
    # p.background_fill_color = "beige"
    # p.background_fill_alpha = 0.5

    p.ygrid.band_fill_color = "olive"
    p.ygrid.band_fill_alpha = 0.1

    p.yaxis[0].formatter = NumeralTickFormatter(format="0.00")

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

def draw_count_chart(data, 
                     fields=['view_count'], 
                     title='Count by Time', 
                     figsize=(12, 6)):
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

