# Hit_or_Not?

Subject: Estimating the number of views for YouTube video

## Getting Started

YouTube is one of the most popular platforms for the music industry. They publish their new songs for promoting. The number of view count is a solid indicator to determine hit or not. Hit or Not is trying to predict the view count in near future for the music videos on *YouTube*.

### Prerequesties

Server
OS - Linux Ubuntu 18.04
Web Server - NGINX
Database - MongoDB
(VM on cloud service is perferred)

Python3  
Jupyter Notebook  
Prophet - Timeseries prediction model by Facebook  
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
* install MONGODB
```
sudo apt install mongodb
```
* for scraping (setup virtual display & firefox)
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
you can install prerequesties python libraires with
```pip install -r requirements.txt```


### Running

Web App - ```$ flask run```
Scraping 
```
$ cd web_scrap/
$ python3 scrap_video_detail.py
$ python3 scrap_view_count.py
```

### Initial Data

Before the run the scraping, it is needed to be set the target videos url to *video_list.txt*

## License

This project is licensed under the GPL3.0 License - see the [LICENSE.md](LICENSE.md) file for details
