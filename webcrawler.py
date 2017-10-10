# -*- coding: utf-8 -*-
"""
Created on Sat Oct  7 07:58:33 2017

@author: 
"""
from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np

req_headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.8',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
}

all_houses = pd.DataFrame()
s = requests.Session()

data = pd.DataFrame()

# Looping over all the pages in a search
for page in range(1,21):
    print ('Scraping page: ', page)
    base_url = 'https://www.zillow.com/homes/for_sale/Los-Angeles-CA/house,condo,apartment_duplex,mobile,townhouse_type/12447_rid/1_pnd/priced_sort/34.630947,-117.47818,33.408516,-119.345856_rect/8_zm/'
    url = base_url + '%s_p/' %(str(page))
    
    # Grabbing the website
    r = s.get(url, headers=req_headers)
    # Parsing
    soup = BeautifulSoup(r.content, 'lxml')
    
    # Finding all the hyper links for homes listed on a page
    url_list = []
    # Looping over links in page
    for hyperlink in soup.find_all('a'):
        href = hyperlink.get('href')
        # Check for string type and key phrase
        if type(href) == str and href[-5:] == 'zpid/':
            url_list.append(href)
        # end 
    # end
    
    for url in url_list:
        sub_url = 'https://www.zillow.com/'+url
        print (sub_url)
                
        sub_r = s.get(sub_url, headers=req_headers)
        sub_soup = BeautifulSoup(sub_r.content, 'lxml')

        # Extracting the address
        full_address = sub_soup.find('h1', {'class': 'notranslate'}).text
        street = full_address.split(',')[0].strip()
        city = full_address.split(',')[1].strip()
        state, zipcode = full_address.split(',')[2].strip().split(' ')        

        # Extracting bed, bath, and square footage
        bed_html, bath_html, sqft_html = sub_soup.find_all('span', {'class': 'addr_bbs'})
        bed, bath, sqft = bed_html.text, bath_html.text, sqft_html.text
        

        
        # Extracting the description
        description = sub_soup.find('div', {'class': 'notranslate zsg-content-item'}).text
                               
        # Extracting the price and Zestimate
        # TO DO: add in way to handle 3 args from amounts (price, price cut, zestimate)
        amounts = [para.text for para in sub_soup.find_all('span', class_='') if '$' in para.text]
        ## Checking to see if there exists both a price and a zestimate value
        if len(amounts) == 1:
            price = amounts.pop()
            zestimate = np.nan
        else: 
            price, zestimate = amounts
            zestimate = int(zestimate.strip().replace('$', '').replace(',', ''))
        # end
        price = int(price.strip().replace('$', '').replace(',', ''))

        row = pd.Series(data = [street, city, state, zipcode, bed, bath, sqft, price, zestimate])
        data = data.append(row, ignore_index=True)
    # end looping over urls in a page
# end looping over pages

data.columns = ['Address', 'City', 'State', 'Zip', 'Bedrooms', 'Bathrooms', 'Sq. Ft.', 'Price', 'Zestimate']