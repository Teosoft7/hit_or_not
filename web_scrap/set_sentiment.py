from pymongo import MongoClient 
from datetime import datetime

from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer

connection = MongoClient()
db = connection['youtube_scrap']

coll = db['comments']
cur = coll.find({ 'sentiment' : { '$exists': False } }).limit(100)
comments = [comment for comment in cur]

for i, comment in enumerate(comments):
    sentiment = TextBlob(comment['comment'], analyzer=NaiveBayesAnalyzer()).sentiment
    coll.update_one({"_id": comment["_id"]}, 
        {"$set": {"sentiment": sentiment.p_pos}})

    print(datetime.now(), i, comment['comment'][:10], sentiment.p_pos)

    