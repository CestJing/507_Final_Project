#################################
##### Name: Jingwen Zhang
##### Uniqname: zhangjw
#################################
from bs4 import BeautifulSoup
import json
import requests
import sqlite3
import sys
import plotly.graph_objects as go 
import secrets as s

class Museum:
    '''a museum

    Instance Attributes
    -------------------
    name: string
        the name of a museum 

    museumtype: string
        the type of the museum

    loation: string
        the location (city/county) of the museum

    description: string
        the brief description of the museum
    '''
    def __init__(self, name, museumtype, location, description):
        self.name = name
        self.museumtype = museumtype
        self.location = location
        self.description = description

    def info(self):
        return self.name + ' (' + self.museumtype + '), ' + self.location + ': ' + self.description

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

def build_state_url_dict():
    ''' Make a dictionary that maps state name to state-museum page url from "https://en.wikipedia.org/wiki"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://en.wikipedia.org/wiki/List_of_museums_in_Michigan', ...}
    '''
    BASE_URL = 'https://en.wikipedia.org'
    STATE_PATH = '/wiki/List_of_museums_in_the_United_States'
    response = requests.get(BASE_URL+STATE_PATH)
    soup = BeautifulSoup(response.text, 'html.parser')

    state_listing = soup.find(class_='multicol').find_all(class_='mw-headline') 
    state_new_list = []
    for i in state_listing:
        state = i.text.lower()
        state_new_list.append(state)

    url_listing = soup.find(class_='multicol').find_all('dl')
    url_new_list = []
    for i in url_listing:
        url = i.find('a')['href']
        url_new_list.append(url)

    state_museum_url_dic = {}
    num = 0
    while num < len(state_new_list):
        state_museum_url_dic[state_new_list[num]] = BASE_URL + url_new_list[num]
        num += 1

    return state_museum_url_dic

def get_museum_instance(museum_list_url):
    '''Make a list of museum instances from a state-museum URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a list of museum in a given state
    
    Returns
    -------
    a list of instance
        a list of museum instance
    '''
    MR_Cache = open_cache()

    if museum_list_url in MR_Cache.keys():
        response = MR_Cache[museum_list_url]
        soup = BeautifulSoup(response, "html.parser")

        museum_listing = soup.find('table', class_='wikitable').find('tbody').find_all('tr')

        num = 1
        museum_instance_list = []
        print('Using Cache')
        while num < len(museum_listing):
            museum = museum_listing[num].find_all('td')

            try:
                name = museum[0].find('a').text.strip()
            except:
                name = museum[0].text.strip()

            try:
                location = museum[1].find('a').text.strip()
            except:
                location = museum[1].text.strip()

            try:
                museumtype = museum[4].find('a').text.strip()
            except:
                museumtype = museum[4].text.strip()

            try:
                description = museum[-1].text.strip()
            except:
                description = museum[-1].find('a').text.strip()

            museum_intance = Museum(name, museumtype, location, description)
            museum_instance_list.append(museum_intance)
            num += 1

    else:
        response = requests.get(museum_list_url).text
        MR_Cache[museum_list_url] = response
        save_cache(MR_Cache)
        soup = BeautifulSoup(response, "html.parser")

        museum_listing = soup.find('table', class_='wikitable').find('tbody').find_all('tr')

        num = 1
        museum_instance_list = []
        print('Fetching')
        while num < len(museum_listing):
            museum = museum_listing[num].find_all('td')

            try:
                name = museum[0].find('a').text.strip()
            except:
                name = museum[0].text.strip()

            try:
                location = museum[1].find('a').text.strip()
            except:
                location = museum[1].text.strip()

            try:
                museumtype = museum[4].find('a').text.strip()
            except:
                museumtype = museum[4].text.strip()

            try:
                description = museum[-1].find('a').text.strip()
            except:
                description = museum[-1].text.strip()

            museum_intance = Museum(name, museumtype, location, description)
            museum_instance_list.append(museum_intance)
            num += 1

    if len(museum_instance_list) > 50:
        museum_instance_list = museum_instance_list[:50]

    return museum_instance_list

def print_museum(museum_instance_list):
    '''Print museum from a museum instance list.
    
    Parameters
    ----------
    museum instance list: list
        a list of museum instances
    
    Returns
    -------
    str
        museums
    '''
    num = 1
    for museum in museum_instance_list:
        print('[',num,'] ', museum.info())
        num +=1

def get_nearby_restaurants(location):
    '''get restaurants from Yelp based on a given location.
    
    Parameters
    ----------
    location: str
    
    Returns
    -------
    list
        a list of restaurant dictionary
    '''
    MR_Cache = open_cache()

    if location in MR_Cache.keys():
        print('Using Cache')
        response = MR_Cache[location]

    else: 
        print('Fetching')
        URL = 'https://api.yelp.com/v3/businesses/search'
        headers = {'Authorization': 'Bearer %s' % s.API_KEY, }
        params = {'term': 'restaurants', 'location': location, 'limit': 50}
        response = requests.get(URL, params=params, headers=headers).json()['businesses']
        MR_Cache[location] = response
        save_cache(MR_Cache)

    restau_list = []
    for restaurant in response:
        restau_dict = {}
        name = restaurant['name']
        restautype = restaurant['categories'][0]['title']
        
        if restaurant['rating'] == '':
            rating = 'no rating'
        else:
            rating = str(restaurant['rating'])

        try:
            price = restaurant['price']
            if price == '':
                price = 'no pricing level'
        except:
            price = 'no pricing level'

        if restaurant['location']['address1'] == '':
            address = 'no address'
        else:
            address = restaurant['location']['address1']

        restau_dict['name'] = name
        restau_dict['restautype'] = restautype
        restau_dict['rating'] = rating
        restau_dict['price'] = price
        restau_dict['address'] = address
        restau_dict['location'] = location.split(',')[0]
        restau_list.append(restau_dict)
    return restau_list

def print_nearby_restaurants(restau_list):
    '''Print restaurants 
    
    Parameters
    ----------
    restau_list: list
        a list of restaurant dictionary 
    
    Returns
    -------
    str
        restaurants near a chosen museum
    ''' 
    new_list = []
    for r in restau_list:
        name = r['name']
        restautype = r['restautype']
        rating = r['rating']
        price = r['price']
        address = r['address']

        restaurant = name + '(' + restautype + '): ' + address + '(' + rating + ', ' + price + ')'
        new_list.append(restaurant)
    
    num = 1
    for restau in new_list:
        print('[',num,'] ', restau)
        num +=1

def create_db():
    '''create a database
    
    Parameters
    ----------
    
    Returns
    -------
    '''
    conn = sqlite3.connect('museum_restaurant.sqlite')
    cur = conn.cursor()

    drop_museums_sql = 'DROP TABLE IF EXISTS "Museums"'
    drop_restaurants_sql = 'DROP TABLE IF EXISTS "Restaurants"'
    
    create_museums_sql = '''
        CREATE TABLE IF NOT EXISTS "Museums" (
            "MuseumName" TEXT NOT NULL, 
            "MuseumType" TEXT NOT NULL,
            "City" TEXT NOT NULL, 
            "Description" TEXT NOT NULL,
            "State" TEXT NOT NULL,
            PRIMARY KEY("MuseumName")
        )
    '''
    create_restaurants_sql = '''
        CREATE TABLE IF NOT EXISTS 'Restaurants'(
            'RestauName' TEXT NOT NULL,
            'RestauType' TEXT NOT NULL,
            'Location' TEXT NOT NULL,
            'Rating' REAL NOT NULL,
            'PricingLevel' TEXT NOT NULL,
            'Address' TEXT NOT NULL,
            'RestauState' TEXT NOT NULL
        )
    '''
    cur.execute(drop_museums_sql)
    cur.execute(drop_restaurants_sql)
    cur.execute(create_museums_sql)
    cur.execute(create_restaurants_sql)
    conn.commit()
    conn.close()

def load_museums(museum_instance_list, state):
    '''insert museum data into sql database
    
    Parameters
    ----------
    museum_instance_list: list
        a list of museum instances
    
    state: str
        a state where museums are located
    
    Returns
    -------
    new database in sql
    '''
    insert_museums_sql = '''
        INSERT INTO Museums
        VALUES (?, ?, ?, ?, ?)
    '''

    conn = sqlite3.connect('museum_restaurant.sqlite')
    cur = conn.cursor()
    for m in museum_instance_list:
        cur.execute(insert_museums_sql,
            [
                m.name,
                m.museumtype,
                m.location, 
                m.description,
                state,
            ]
        )
    conn.commit()
    conn.close()

def load_restaurants(restau_list, state):
    '''insert restaurant data into sql database  
    
    Parameters
    ----------
    restau_list: list
        a list of restaurant dictionary

    state: str
        a state where the restaurants are located
    
    Returns
    -------
    new database in sql
    '''
    insert_restaurants_sql = '''
        INSERT INTO Restaurants
        VALUES (?, ?, ?, ?, ?, ?, ?)
    '''

    conn = sqlite3.connect('museum_restaurant.sqlite')
    cur = conn.cursor()
    for r in restau_list:
        cur.execute(insert_restaurants_sql,
            [
                r['name'],
                r['restautype'],
                r['location'],
                r['rating'], 
                r['price'],
                r['address'],
                state,
            ]
        )
    conn.commit()
    conn.close() 

def plot(restau_list):
    '''open a web page with a histogram showing the restaurants and the rating
    
    Parameters
    ----------
    restau_list: list
        a list of restaurant dictionaries
    
    Returns
    -------
    a web page with a histogram
    '''
    restaurant = []
    rating = []
    for r in restau_list:
        name = r['name']
        restaurant.append(name)
        rate = r['rating']
        rating.append(rate)

    bar_data = go.Bar(x=restaurant, y=rating)
    basic_layout = go.Layout(title="Nearby Restaurants and the Rate")
    fig = go.Figure(data=bar_data, layout=basic_layout)

    fig.show()


if __name__ == "__main__":

    create_db()

    query = input('Enter a state name (e.g. Michigan, michigan) or "exit": ')

    while query.lower() == 'exit':
        sys.exit()
     
    while query.lower() != 'exit':
        if query.lower() not in build_state_url_dict().keys():
            print('[Error] Enter proper state name') 
            query = input('Enter a state name (e.g. Michigan, michigan) or "exit": ')

        elif query.lower() in build_state_url_dict().keys():
            state_url = build_state_url_dict()[query.lower()]
            museum_list = get_museum_instance(state_url)
            load_museums(museum_list, query)
            print('-----------------------------------')
            print('List of museums in', query)
            print('-----------------------------------')
            print_museum(museum_list)

            query2 = input('Choose the number for detail search or "exit" or "back": ')

            while query2.isdigit():
                if int(query2) > len(museum_list) or int(query2) < 1:
                    print('[Error] Invalid input')
                    query2 = input('Choose the number for detail search or "exit" or "back": ')

                elif int(query2) <= len(museum_list):
                    museum_instance = museum_list[int(query2)-1]
                    location = museum_instance.location + ', ' + query.lower()
                    nearby_restaurants_dict = get_nearby_restaurants(location)
                    load_restaurants(nearby_restaurants_dict, query)
                    print('-----------------------------------')
                    print('Places near', museum_instance.name)
                    print('-----------------------------------')
                    print_nearby_restaurants(nearby_restaurants_dict)
                    plot(nearby_restaurants_dict)
                    query2 = input('Choose the number for detail search or "exit" or "back": ')

            if query2 == 'back':
                query = input('Enter a state name (e.g. Michigan, michigan) or "exit": ')
            elif query2 == "exit":
                sys.exit()














