from bs4 import BeautifulSoup
import json
import requests
import sqlite3
import plotly
import secrets as s

CACHE_FILENAME = "cache.json"

def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close() 

URL = 'https://api.yelp.com/v3/businesses/search'
headers = {'Authorization': 'Bearer %s' % s.API_KEY, }
params = {'term': 'restaurants', 'location': 'Lansing, Michigan', 'limit': 50}
response = requests.get(URL, params=params, headers=headers).json()['businesses']

filepath='yelp_response'
with open(filepath, 'w', encoding='utf-8') as file_obj:
    json.dump(response, file_obj, indent=2)

print(len(response))




# BASE_URL = 'https://en.wikipedia.org/wiki'
# List_state = '/List_of_museums_in_the_United_States'
# response = requests.get(BASE_URL+List_state)
# soup = BeautifulSoup(response.text, 'html.parser')

# state_url_listings = soup.find(class_='multicol').find_all('dl')
# # print(soup)
# state_museum_url_dict = {}
# for state_url_listing in state_url_listings:
#     state_name = state_url_listing.find('a').text[19:]
#     museum_listing_url = state_url_listing.find('a')['href']
#     state_museum_url_dict[state_name] = museum_listing_url

# print(state_museum_url_dict)


# def create_db():
#     conn = sqlite3.connect('museum_restaurant.sqlite')
#     cur = conn.cursor()

#     drop_museums_sql = 'DROP TABLE IF EXISTS "Museums"'
#     drop_restaurants_sql = 'DROP TABLE IF EXISTS "Restaurants"'
    
#     create_bars_sql = '''
#         CREATE TABLE IF NOT EXISTS "Museums" (
#             "MuseumName" TEXT NOT NULL, 
#             "MuseumType" TEXT NOT NULL,
#             "City" TEXT NOT NULL, 
#             "Description" TEXT NOT NULL,
#         )
#     '''
#     create_restaurants_sql = '''
#         CREATE TABLE IF NOT EXISTS 'Restaurants'(
#             'RestauName' TEXT NOT NULL,
#             'RestauType' TEXT NOT NULL,
#             'Location' TEXT NOT NULL,
#             'Rating' REAL NOT NULL,
#             'PricingLevel' TEXT NOT NULL,
#             'Address' TEXT NOT NULL,
#         )
#     '''
#     cur.execute(drop_museums_sql)
#     cur.execute(drop_restaurants_sql)
#     cur.execute(create_museums_sql)
#     cur.execute(create_restaurants_sql)
#     conn.commit()
#     conn.close()

# create_db()

# def load_museums():

