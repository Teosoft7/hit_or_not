# Hit_or_Not?

Subject: Estimating the number of views for YouTube video (especially Official Music Video)

## YouTube View Predictor

YouTube is one of the most important platforms for the music industry. They publish their new songs for promoting. If it is going to be popular, the number of views, likes, comments are increasing also. Based on these kinds of data, is it possible to know it is going to be popular or not earlier with data science methods?

With the number of views, number of comments, number of likes and the sentiment of comments for some duration, it could be built a prediction model for the number of views. 

Set the web scraper to cloud server, run it regularly (maybe every a couple of mins), collect new videos with #musicvideo hashtag & under 5mins length. Collect # of views, comments, likes and the sentiment score for comments for the certain video and store it to the mongodb database.

By using some regression model (linear, decision tree, random forest, ...) to predict the # of views. Also, consider Prophet model because the data has a timestamp. For sentiment analysis, it is going to select a pre-trained NLP model.

Basically, train/test split with collected data and try to find a real-world example, 'select a music video and tracing its rank of Billboard or something like that'.  

The model will be deployed as a Web app that can be used to select a video from the list to see the prediction results

#### cf) This app is currently under construction!!!
