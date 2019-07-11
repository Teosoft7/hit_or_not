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

def collect_video_detail(browser, urls, start_point=0):    
    """Scrap video detail from youtube and store to DB"""
    i = 0
    print(f'collecting start - {datetime.now()}')

    for url in urls:
        # if some skip needed
        # set start_point in the list
        if (i < start_point):
            i+=1
            continue
        
        try:            
            coll = db['video_detail']
            print(f'{datetime.now()} {i}: {url}')
            # open the web page
            browser.get(url)
            time.sleep(3)

            browser.execute_script("window.scrollTo(0, window.scrollY + 720)")
            time.sleep(3)

            # parsing the values
            title = browser.find_element_by_css_selector('h1.title').text
            published = browser.find_element_by_css_selector('span.date').text
            video_id = url.split('=')[-1]

            video_info = {
                'video_id': video_id,
                'published': published,
                'title': title,
                'url': url
            }

            coll.insert_one(video_info)
            print(f'{datetime.now()} {i} - {title} has been processed.')
            i += 1
        except:
            print(f'some errors happens for {url}')
        
    print(f'collecting end - {datetime.now()}')

# Open files & Get URLs
with open('./data/video_list.txt', 'r') as f:
    urls = f.readlines()

# set browser to headless
options = Options()
options.headless = True

# setup virtual display
with Display(visible=1, size=(1920, 1080)) as display:
    # initialize browser
    browser = webdriver.Firefox(options=options)
    browser.maximize_window()
    
    collect_video_detail(browser, urls, start_point=0)
    browser.close()