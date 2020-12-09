
# initialize modules -----------------------------------

from bs4 import BeautifulSoup as bs
from webdriver_manager.chrome import ChromeDriverManager
from splinter import Browser
from pprint import pprint
import pymongo
import requests
import pandas as pd
import html5lib

#-------------------------------------------------------

def init_browser():
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)
    return browser
def scrape():
    browser = init_browser()
    mars_collection = {}
    
    # Mars News --------------------------------------------------------
    url1 = "https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest"
    response1 = requests.get(url1)
    soup1 = bs(response1.text, 'html.parser')

    #finding news_title
    title_code = soup1.find('div', class_="content_title")
    news_title = title_code.find('a').text
    mars_collection["news_title"] = news_title
    #finding news_paragraph
    paragraph_code = soup1.find('div', class_="rollover_description")
    news_paragraph = paragraph_code.find('div', class_="rollover_description_inner").text
    mars_collection["news_paragraph"] = news_paragraph


    # Mars Feature Image-------------------------------------------------
    url2 = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url2)

    try:
        browser.links.find_by_partial_text('FULL IMAGE').click()
        browser.links.find_by_partial_text('more info').click()
        url3 = browser.url
    except:
        print("button not found")

    response2 = requests.get(url3)
    soup2 = bs(response2.text, 'html.parser')

    picture_code = soup2.find('figure', class_= "lede")
    picture_url = picture_code.find('a').get('href')

    featured_image_url = 'https://www.jpl.nasa.gov' + str(picture_url)
    browser.visit(featured_image_url)
    mars_collection["featured_image_url"] = featured_image_url


    # Mars Facts --------------------------------------------------------
    url4 ='http://space-facts.com/mars/'
    tables = pd.read_html(url4)
    mars_table = tables[0]
    mars_table = mars_table.rename(columns = {0: "Facts", 1: "Values"})

    mars_table_html = mars_table.to_html(index = False)
    mars_table_html = mars_table_html.replace("\n", "")
    mars_collection["fact_table"] = mars_table_html


    # Mars Hemispheres --------------------------------------------------
    url5 = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(url5)

    response3 = requests.get(url5)
    soup3 = bs(response3.text, 'html.parser')

    hemispheres = soup3.find_all('h3')
    hemi_name_list =[]
    for hemisphere in hemispheres:
        name = hemisphere.text
        name = name.replace(" Enhanced", "")
        hemi_name_list.append(name)

    hemi_img_list =[]
    results = soup3.find_all('div', class_="item")
    url_source = "http://astrogeology.usgs.gov"
    for result in results:
        link = result.find("a")
        link = link.get('href')
        result_link = url_source + link
        browser.visit(result_link)
        page_url = browser.url
        response_change = requests.get(page_url)
        soup_change = bs(response_change.text, 'html.parser')
        link2 = soup_change.find('li')
        img_url = link2.find('a').get('href')
        hemi_img_list.append(img_url)
        
    hemisphere_image_urls = []
    for x in range(len(hemi_name_list)):
        dict_entry = {}
        name = hemi_name_list[x-1]
        img = hemi_img_list[x-1]
        dict_entry['title'] = name
        dict_entry['img_url'] = img
        hemisphere_image_urls.append(dict_entry)

    mars_collection["hemisphere_images"] = hemisphere_image_urls
    return mars_collection