# libaries for getting data
from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import datetime
import os
from telegram_bot import telegram_send_text

def get_soup(url):
    page = requests.get(url).text
    soup = BeautifulSoup(str(page), 'html.parser')
    return soup

def get_item_urls(url):
    soup = get_soup(url)
    links = soup.find_all('a', class_ = 'listing-search-item__link listing-search-item__link--title')
    links = [''.join('https://www.pararius.com' + link['href']) for link in links]
    return links

def parse_item(url):
    soup = get_soup(url)
    try:
        title = soup.find('h1', class_ = 'listing-detail-summary__title').get_text().replace('For rent: ', '').replace('Apartment ', '').replace('House ','').strip()
    except:
        title = None
    try:
        price = int(soup.find('div', class_ = 'listing-detail-summary__price').get_text().replace('€','').replace(',','').replace(' per month','').strip())
    except:
        price = None
    try:
        features = soup.find_all('dd', class_ = 'illustrated-features__description')
    except:
        features = None
    try:
        features = [x.get_text().strip() for x in features]
    except:
        features = None
    try:
        surface = int(features[0].replace(' m²', '').strip())
    except:
        surface = None
    try:
        bedrooms = int(soup.find('dd', class_ = 'listing-features__description listing-features__description--number_of_bedrooms').get_text().strip())
    except:
        bedrooms = None
    #description = soup.find('div', class_ = 'listing-detail-description__description').get_text().replace('More', '').replace('Description','').strip()
    try:
        bedroom_price = round(price / bedrooms)
    except:
        bedroom_price = None
    try:    
        date_offered = soup.find('dd', class_ = 'listing-features__description listing-features__description--offered_since').get_text().strip()
    except:
        date_offered = None
    try:
        available_from = soup.find('dd', class_ = 'listing-features__description listing-features__description--acceptance').get_text().strip()
    except:
        available_from = None
    try:
        dwelling_type = soup.find('dd', class_ = 'listing-features__description listing-features__description--dwelling_type').get_text().strip()
    except:
        dwelling_type = None
    try:
        facilities = soup.find('dd', class_ = 'listing-features__description listing-features__description--facilities').get_text().strip()
    except:
        facilities = None
    try:
        estate_agent = soup.find('a', class_ = 'agent-summary__name-link').contents[0].strip()
    except:
        estate_agent = None
    try:
        location = soup.find('div', class_ = 'listing-detail-summary__location').get_text().strip()
    except:
        location = None
    try:
        new = soup.find('span', class_ = 'listing-detail-summary__is-new').get_text().strip()
    except:
        new = None
    item = {
            'url': url,
            'title': title,
            'bedroom_price': bedroom_price,
            'bedrooms': bedrooms,
            'location': location,
            'surface': surface,
            'dwelling_type': dwelling_type,
            'facilities': facilities,
            'date_offered': date_offered,
            'available_from': available_from,
            'estate_agent': estate_agent,
            'price': price,
            'new': new
        }
    return item

def parse_pages(city):
    items = []
    page = 1
    while True:
        url = "https://www.pararius.com/apartments/" + str(city).lower() +"/page-" + str(page)
        print('Page ' + str(page))
        page += 1
        item_urls = get_item_urls(url)
        for item_url in item_urls:
            items.append(parse_item(item_url))
        if len(item_urls) == 0:
            break
    df = pd.DataFrame(items)
    return df

def filtering(df):
    # Avoid estate agents with bad data quality
    avoid_estate_agents = ['Vesteda Zuid West','Vesteda West', 'Vesteda Midden', 'NOORD', 'Vesteda Noord West', 'AMSTERDAM REGIO', 'Vesteda Oost', 'Parker & Williams Real Estate Services']
    df = df.query("estate_agent != " + str(avoid_estate_agents))
    df = df.loc[df['bedroom_price'] <= 500]
    return df

def notify(df, file_name, chat_id='-264163246'):
    with open(file_name, 'r') as f:
        for ind in df.index:
            if any(df['url'][ind] in line for line in f):
                pass # known id
            else:
                print('New house')
                telegram_send_text('New house: ' + df['url'][ind], chat_id)
                break
    return

# Deduplicate item list, sort values on price and create file from all items
def save_to_csv(df, city):
    df.index.name='item depth'
    df = df.drop_duplicates()
    df = df.sort_values('bedroom_price',ascending=True)
    try:
        os.mkdir(str(os.getcwd()) + '/data')
    except OSError:
        pass
    file_new = os.getcwd() + '/data/' + city + '_apartments.csv'
    df.to_csv(file_new)
    return df

def check(city):
    df = parse_pages(city)
    df = filtering(df)
    filename = os.getcwd() + '/data/' + city + '_apartments.csv'
    notify(df, filename)
    save_to_csv(df, city)
    return

check('Haarlem')