from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from pyvirtualdisplay import Display 
from datetime import datetime
from pymongo import MongoClient 

import time
import random

# Connect to Mongo Database
connection = MongoClient()
db = connection['youtube_scrap']

# Function for get view count
def get_view_count(browser, url):
    """Return the view_count and timestamp"""
    browser.get(url)
    time.sleep(2 + random.randint(0, 4))
    now = datetime.now()
    sel = 'span.view-count'
    view_count = browser.find_element_by_css_selector(sel).text

    return {
        'view_count': int(''.join([n for n in view_count if n.isdigit()])),
        'timestamp': now }

# Get list of videos to collect view counts
coll = db['videos']
cur = coll.find({})
videos = [video for video in cur]

# set browser to headless
options = Options()
options.headless = True

# setup virtual display
with Display(visible=1, size=(1280, 800)) as display:
    # initialize browser
    browser = webdriver.Firefox(options=options)
    browser.maximize_window()

    count_coll = db['view_count']

    # loop through forever
    while True:
        for i, video in enumerate(videos):
            url = video['url']
            count = get_view_count(browser, url)
            print(i, ': ', video['title'], ' - ',count['view_count'])
            
            count_coll.insert_one({
                'title': video['title'],
                'view_count': count['view_count'],
                'timestamp': count['timestamp']
            })
        # Idle 5 mins
        time.sleep(300)

browser.close()
