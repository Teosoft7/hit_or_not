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
    time.sleep(1 + random.randint(0, 4))
    now = datetime.now()

    browser.execute_script("window.scrollTo(0, window.scrollY + 640)")
    time.sleep(4)

    # view-count
    sel = 'span.view-count'
    view_count_element = browser.find_element_by_css_selector(sel).text
    count = ''.join([n for n in view_count_element if n.isdigit()])
    view_count = int(count) if len(count) > 0 else 0
    
    # number of likes
    like_sel = 'ytd-toggle-button-renderer.style-text[is-icon-button] #text.ytd-toggle-button-renderer'
    like_count_element = browser.find_element_by_css_selector(like_sel).get_attribute('aria-label')
    if len(like_count_element) > 0:
        like = ''.join([n for n in like_count_element if n.isdigit()])
        like_count = int(like) if len(like) > 0 else 0

    # number of comments
    class_name = 'count-text'
    count_text_element = browser.find_element_by_class_name('count-text').text
    comment = ''.join([n for n in count_text_element if n.isdigit()])
    comment_count = int(comment) if len(comment) > 0 else 0

    return {
        'view_count': view_count,
        'comment_count': comment_count,
        'like_count': like_count,
        'timestamp': now }

# Get list of videos to collect view counts
coll = db['videos']
cur = coll.find({})
videos = [video for video in cur]
random.shuffle(videos)

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
            print(i, ': ', video['title'], ' - ', url)
            print(count)

            count_coll.insert_one({
                'title': video['title'],
                'view_count': count['view_count'],
                'comment_count': count['comment_count'],
                'like_count': count['like_count'],
                'timestamp': count['timestamp']
            })
        # Idle 1+ mins
        time.sleep(60 + random.randint(0, 60))

browser.close()
