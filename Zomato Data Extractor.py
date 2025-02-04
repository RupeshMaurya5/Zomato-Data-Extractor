#!/usr/bin/env python
# coding: utf-8

# In[148]:


from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
import time
import pandas as pd


# In[149]:


url = 'https://www.zomato.com/ncr/delivery-in-najafgarh'
s = Service("C:/chromedriver-win64/chromedriver.exe")


# In[150]:


driver = webdriver.Chrome(service = s)
driver.get(url)
time.sleep(6)


# In[151]:


height = driver.execute_script("return document.body.scrollHeight")


# In[152]:


while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(6)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if height == new_height:
        break
    height = new_height


# In[153]:


html = driver.page_source


# In[154]:


import requests


# In[155]:


session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://www.zomato.com/'
})

response = session.get(url)
print(response.status_code)


# In[156]:


soup = BeautifulSoup(html, 'html.parser')


# In[157]:


containers = soup.find_all('div', class_='jumbo-tracker')
len(containers)


# In[158]:


base_url = 'https://www.zomato.com'


# In[159]:


# Lists to hold restaurant names and URLs
res_names = []
res_urls = []

for container in containers:
    # Extract the restaurant name
    res_name_tag = container.find('h4')  # Adjust the tag if necessary
    if res_name_tag is not None:
        res_name = res_name_tag.text.strip()
    else:
        res_name = ''  # Default to empty string if name is not found

    # Extract the restaurant URL
    url_tag = container.find('a')  # Assuming the URL is within an a tag
    if url_tag and 'href' in url_tag.attrs:
        relative_url = url_tag['href']
        absolute_url = base_url + relative_url if relative_url else ''
    else:
        absolute_url = ''  # Default to empty string if URL is not found

    # Only append if the restaurant name is not empty
    if res_name:
        res_names.append(res_name)
        res_urls.append(absolute_url)
    else:
        print(f"Skipped entry with empty name. URL: {absolute_url}")  # Log the skipped entry

# Ensure both lists have the same length
if len(res_names) != len(res_urls):
    print("Warning: Mismatch in lengths of res_names and res_urls")
    print(f"Length of res_names: {len(res_names)}, Length of res_urls: {len(res_urls)}")


# In[160]:


df_restaurants = pd.DataFrame({
    'name': res_names,
    'url': res_urls
})


# In[161]:


len(df_restaurants)


# In[162]:


res_location = []


# In[163]:


# Start a session for requests
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://www.zomato.com/'
})


# In[164]:


# Loop over each restaurant URL in the DataFrame
total_urls = len(df_restaurants['url'])
for idx, url in enumerate(df_restaurants['url'], start=1):
    try:
        # Fetch the restaurant page
        response = session.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the container with the address
            containers = soup.find_all('div', {'class': 'sc-fOICqy fPpMAv'})

            # Extract the address
            for container in containers:
                address_tag = container.find('a', {'class': 'sc-clNaTc vNCcy'})
                address = address_tag.text.strip() if address_tag else 'Address not available'
                
                res_location.append(address)
                print(f"Address: {address}")
        else:
            res_location.append('Failed to retrieve page')
            print(f"Failed to fetch {url} with status code {response.status_code}")

    except requests.exceptions.RequestException as e:
        res_location.append('Error fetching address')
        print(f"Error fetching {url}: {e}")

    # Print progress
    print(f"Processed {idx}/{total_urls} URLs")


# In[165]:


# Create a new DataFrame with URLs and addresses
df_addresses = pd.DataFrame({
    'url': res_urls,
    'address': res_location
})


# In[166]:


df_final = pd.merge(df_restaurants, df_addresses, on='url')


# In[167]:


df_final.to_excel('Najafgarh Rest zomato.xlsx', index = False)


# In[168]:


driver.quit()

