from pymongo import MongoClient, DESCENDING

from bokeh.models import (HoverTool, FactorRange, Plot, LinearAxis, Grid,
                          Range1d)
from bokeh.models.glyphs import VBar
from bokeh.plotting import figure
from bokeh.models.sources import ColumnDataSource
from bokeh.sampledata.stocks import AAPL

import numpy as np

def get_last4_videos(db):
    """Return the last 4 video in the db"""
    video_coll = db['video_detail']
    view_coll = db['view_count']
    cursor = video_coll.find({}).sort('title', -1).limit(4)

    result = []
    for video in cursor:
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

def get_view_data(db, video_id):
    """Return view_count collection for video_id"""
    view_count_coll = db['view_count']
    filter = {'video_id': video_id}
    cursor = view_count_coll.find(filter).sort('timestamp', DESCENDING)

    return [record for record in cursor]

def create_chart(data, title, hover_tool=None,
                     width=720, height=360):
    """Create a line chart with data
    """
    tools = []
    if hover_tool:
        tools = [hover_tool,]

    counts = np.array([row['view_count'] for row in data])
    
    label=''
    if counts.min() > 1_000_000:
        counts = counts / 1_000_000
        label = ' (M)'
    elif counts.min() > 1_000:
        counts = counts / 1_000
        label = ' (K)'

    times = [row['timestamp'] for row in data]
    p = figure(plot_width=width, 
               plot_height=height,
               x_axis_type="datetime")
               
    p.line(times, counts, line_width=2, color='navy', legend='view counts')

    p.title.text = "View Counts"
    p.legend.location = "top_left"
    p.grid.grid_line_alpha = 0
    p.xaxis.axis_label = 'Date'
    p.yaxis.axis_label = 'Views' + label
    p.ygrid.band_fill_color = "olive"
    p.ygrid.band_fill_alpha = 0.1

    return p