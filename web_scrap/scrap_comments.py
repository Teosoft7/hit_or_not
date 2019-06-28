from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from pyvirtualdisplay import Display 
from pymongo import MongoClient 
from datetime import datetime

import time
import random

connection = MongoClient(port=47017)
db = connection['youtube_scrap']

coll = db['video_detail']
cur = coll.find({'has_comment': 'N'})
videos = [video for video in cur]
random.shuffle(videos)

print(len(video))

def get_comments(browser, db, url):
    """Get comments for video(url), and store it to database"""
    browser.get(url)
    time.sleep(2)

    for _ in range(20):
        browser.execute_script("window.scrollTo(0, window.scrollY + 720)")
        time.sleep(1)

    comments = browser.find_elements_by_id('content-text')
    video_id = url.split('=')[-1]

    for comment in comments:
        text = comment.text
        coll = db['comments']
        coll.insert_one({
            'video_id': video_id,
            'comment': text
        })
    
    print(f'{datetime.now()} - {video_id} : {len(comments)} stored.')