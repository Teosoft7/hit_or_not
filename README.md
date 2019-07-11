# Hit or Not?

**Keeping track of music video on YouTube**
[http://music.proba.in](http://music.proba.in)


## Getting Started

YouTube is one of the most popular platforms for music artists. They publish their new songs to YouTube for promoting. The number of view count is a solid indicator to determine hit or not. Hit or Not is trying to predict the view count in the near future for the music videos on *YouTube*.


## Data Preparation

Even though YouTube is providing APIs with a lot of limitations, to keep track of changing of view count for video, it is needed to scrap the data by ourselves. With selenium and Firefox, we can collect general information for video and view counts.

![YouTube Screen](common/images/youtube.png?raw=true "YouTube Screen")



## Modeling

The change of view/like/comments has correlation and could be used for the data model. But view increments is definitely based on the time series. It is better to use facebook's **[Prophet](https://facebook.github.io/prophet/)** model for prediction. Prophet is a procedure for forecasting time series data based on an additive model where non-linear trends. It is fast and provides completely automated forecasts.  

![View vs Like](common/images/viewvslike.png?raw=true "View vs Like")

The final goal is to build a classification model for the hit or not with collecting much more data.


## Let's make the app working

### Prerequisites for App

Server
OS - Linux Ubuntu 18.04
Web Server - NGINX
Database - MongoDB
(VM on cloud service is preferred)

Python3
Jupyter Notebook
Prophet - Time series prediction model by Facebook
Flask - Web App Framework
Bokeh - Visualization library
Selenium - Web scraping
Pandas, Numpy, ... - Python library for data science
Bootstrap4 - CSS Library
Material Dashboard by Creative Tim ([Link](https://github.com/creativetimofficial/material-dashboard))

### Install & Setup

**for Server**
* install NGINX
```
sudo apt install nginx
```
* install MongoDB
```
sudo apt install mongodb
```
* for scraping (setup virtual display & Firefox)
```
## Firefox
sudo apt update
sudo apt install firefox

## Geckodriver
wget https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz
sudo sh -c 'tar -x geckodriver -zf geckodriver-v0.24.0-linux64.tar.gz -O > /usr/bin/geckodriver'
sudo chmod +x /usr/bin/geckodriver
rm geckodriver-v0.24.0-linux64.tar.gz

## Virtual display
sudo apt install xvfb
sudo apt-get install xserver-xephyr
```

With attached requirements.txt file,
you can install prerequisites python libraries with
```pip install -r requirements.txt```

### Initial Data

Before the run the scraping, it is needed to be set the target videos url to *video_list.txt*

### Running the scrapping

```
$ cd web_scrap/
$ python3 scrap_video_detail.py
$ python3 scrap_view_count.py
```
Scraping video_detail takes a while,
but scraping view_count needs to be run forever.
(If you want to keep track of change of view count)

### Running the web app

On the Linux Server

```
$ cd web_app
$ FLASK_APP=app.py flask run
```


## License

This project is licensed under the GPL3.0 License - see the [LICENSE.md](LICENSE.md) file for details
