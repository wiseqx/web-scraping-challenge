from bs4 import BeautifulSoup as bs
import requests
from splinter import Browser
import pandas as pd
from flask import Flask, render_template
from selenium import webdriver
import re
import time


def init_browser():
    executable_path = {'executable_path': 'chromedriver.exe'}
    return Browser("chrome", **executable_path, headless=False)


def scrape():
    mars_data = {}
    # Mars news
    news_url = 'https://mars.nasa.gov/news'
    news_response = requests.get(news_url)
    news_soup = bs(news_response.text, 'html.parser')
    news_title = news_soup.find("div", class_="content_title").text.strip()
    news_p = news_soup.find("div", class_="rollover_description_inner").text.strip()
    
    
    # Featured Images
    browser = init_browser()
    
    image_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(image_url)
    time.sleep(2)
    
    image_html = browser.html
    img_soup = bs(image_html, 'html.parser')
    
    images = img_soup.find_all('a', class_ = "fancybox")
    
    url_li=[]
    for image in images:
        href = image['data-fancybox-href']
        if 'largesize' in href:
            image_url = 'https://www.jpl.nasa.gov' + href
            url_li.append(image_url)
            
    featured_image_url = url_li[0]
    
    
    browser.quit()
    
    
    # Mars Weather
    twitter_url = 'https://twitter.com/marswxreport?lang=en'
    twitter_response = requests.get(twitter_url)
    twitter_soup = bs(twitter_response.text, 'html.parser')
    
    weather_text = twitter_soup.find_all("div", class_="js-tweet-text-container")
    weather_tweets = []
    for weather in weather_text:
        tweet = weather.text
        weather_tweets.append(tweet)

    mars_weather = re.sub(r'pic.twitter.com\S+', '', weather_tweets[0].replace('\n',' ').lstrip())
    
    
    
    # Mars Facts
    facts_url = "https://space-facts.com/mars/"
    tables = pd.read_html(facts_url)
    df = tables[0]
    df.columns = ['description', 'value']
    html_table = df.to_html(index=False)
    
    
    
    # Mars Hemisphere
    hemisphere_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    hemisphere_response = requests.get(hemisphere_url)
    hemisphere_soup = bs(hemisphere_response.text, 'html.parser')

    
    high_res_images = hemisphere_soup.find_all('a', class_="itemLink product-item")
    
    
    hemisphere_image_urls =[]

    for image in high_res_images:
        image_dict = {}

        title = image.find('h3').text
        image_dict['title'] = title.strip(' Enhanced')

        temp_img_url = image['href']

        # scrape the website
        new_image_url = 'https://astrogeology.usgs.gov' + temp_img_url
        img_request = requests.get(new_image_url)
        full_img_soup = bs(img_request.text, 'lxml')
        img_tag = full_img_soup.find('div', class_ = 'downloads')
        img_url = img_tag.find('a')['href']
        image_dict['img_url'] = img_url


        hemisphere_image_urls.append(image_dict)
    

    # make a dictionary
    mars_data = {
        "news_title": news_title,
        'news_p' : news_p,
        'featured_image_url' : featured_image_url,
        'mars_current_weather' : mars_weather,
        'fact_table' : html_table,
        'hemisphere_image_urls' : hemisphere_image_urls
    }
        

    
    return mars_data
    
    
