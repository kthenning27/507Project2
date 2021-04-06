#################################
##### Name: Katie Henning
##### Uniqname: khenning
#################################

from bs4 import BeautifulSoup
import requests
import json

import secrets # file that contains your API key


CACHE_FILENAME = "nps_cache.json"
CACHE_DICT = {}

client_key = secrets.MAPQUEST_API_KEY
client_secret = secrets.MAPQUEST_API_SECRET

def printer():
    print("Hello, World!")

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


class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    def __init__(self, category, name, address, zipcode, phone):
        self.category = category
        self.name = name 
        self.address = address
        self.zipcode = zipcode
        self.phone = phone

    def info(self):
        return f'{self.name} ({self.category}) : {self.address} {self.zipcode}'


def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    BASE_URL = "https://www.nps.gov"
    response = requests.get("https://www.nps.gov/index.htm")
    soup = BeautifulSoup(response.text, 'html.parser')
    
    
    state_url_dict = {}

    state_link_parent = soup.find('ul', class_ = "dropdown-menu SearchBar-keywordSearch")
    state_link_lis = state_link_parent.find_all('li', recursive = False)
    for state_link_li in state_link_lis:
        state_li = state_link_li.find('a')
        state_link_tag = state_li['href']
        state_link_url = BASE_URL + state_link_tag
        state_name = state_li.text
        state_url_dict[state_name.lower()] = state_link_url
    return state_url_dict
 


def get_site_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance
    '''
    # for site_url in 
    response = requests.get("https://www.nps.gov" + site_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    site_title_div = soup.find("div", class_ = "Hero-titleContainer clearfix")
    site_title_class = site_title_div.find("a", class_ = "Hero-title")
    site_category_div = soup.find("div", class_ = "Hero-designationContainer")
    site_category_span = site_category_div.find("span", class_ = "Hero-designation")
    if not site_category_span or site_category_span.text.strip() == '':
        site_category_name = "No category"
    else:
        site_category_name = site_category_span.text
    site_title_name = site_title_class.text
    site_address_city_span = soup.find("span", itemprop = "addressLocality")
    if not site_address_city_span:
        site_address_city_text = "No address"
    else:
        site_address_city_text = site_address_city_span.text.strip()

    site_address_region_span = soup.find("span", itemprop = "addressRegion")
    if not site_address_region_span:
        site_address_region_text = "No state"
    else:
        site_address_region_text = site_address_region_span.text.strip()

    site_zipcode_span = soup.find("span", itemprop = "postalCode")
    if not site_zipcode_span:
        site_zipcode_text = "No zipcode"
    else:
        site_zipcode_text = site_zipcode_span.text.strip()

    site_phone_number_span = soup.find("span", itemprop ="telephone")
    if not site_phone_number_span:
        site_phone_number_text = "No phone number"
    else:
        site_phone_number_text = site_phone_number_span.text.strip()

    site_address = site_address_city_text + ", " + site_address_region_text

    site_instance  = NationalSite(site_category_name, site_title_name, site_address, site_zipcode_text, site_phone_number_text)

    return site_instance

def make_url_request_using_cache(url, CACHE_DICT):
    ''''makes use of the cache_dict to check if the URL
    has been searched for before


    Parameters
    ----------
    url: sting
        the url searched for in the cahe dict
    CACHE_DICT: dict
        the json file with cached information
    -------
    dict key
        the key in the CAHE_DICT corresponsing to the URL in json format

    '''
    if url in CACHE_DICT.keys():
        print("using cache")
        return CACHE_DICT[url]
    else:
        print ("Fetching")
        response = requests.get(url)
        CACHE_DICT[url] = response.text
        save_cache(CACHE_DICT)
        return CACHE_DICT[url]


def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    response = make_url_request_using_cache(state_url, CACHE_DICT)
        
    soup = BeautifulSoup(response, 'html.parser')

    sites_url_div = soup.find("div", id= "parkListResultsArea")
    sites_url_li = sites_url_div.find_all("li")
    national_site_instance_list = []
    for li in sites_url_li:
        site_header = li.find("h3")
        if site_header:
            site_a = site_header.find("a")
            site_link = site_a['href']
            site_instance = get_site_instance(site_link + "index.htm")
            national_site_instance_list.append(site_instance)
    return national_site_instance_list

def display_national_sites(national_site_instance_list):
    '''formats the response from the API for the display list

    

    Parameters
    ----------
    national_site_instance_list: list
        the list of national site instances made from the function
        get_sites_for_state
    Returns
    -------
    list
        the display list needed to index the national sites for the iser response

    '''
    counter = 0
    display_list = []
    for national_site_instance in national_site_instance_list:
        counter += 1
        #display_format = f'{[counter]} {national_site_instance.info()}' 
        display_list.append(national_site_instance)
        print(f'{[counter]} {national_site_instance.info()}')
    return display_list

    
def make_map_quest_request_using_cache(site_object, CACHE_DICT, param_dict, BASE_URL):
    '''makes use of the cache_dict to check if the zip code
    has been searched for before


    Parameters
    ----------
    site_object: Class object
        the site object the searched is based off of
    CACHE_DICT: dict
        the json file with cached information
    param_dict: dict
        the other info needed for the API
    BASE_URL : str
        the basis of the url needed to make the API reqyest
    Returns
    -------
    dict key
        the key in the CAHE_DICT corresponsing to the URL in json format

    '''
    # Determine if request for data has already been made, if so return result from cache dictionary
    for key in CACHE_DICT.keys():
        if site_object.zipcode in key:
            print("using cache")
            return CACHE_DICT[key]

    # If not, make the request, save it, then return the result.
    print ("Fetching")
    response = requests.get(BASE_URL, params=param_dict)
    CACHE_DICT[response.url] = response.json()
    save_cache(CACHE_DICT)
    return CACHE_DICT[response.url]

def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''


    BASE_URL = "http://www.mapquestapi.com/search/v2/radius"
    param_dict = {'key': client_key, 'origin': site_object.zipcode,  'radius': 10 , 'units' : 'm' ,  'maxMatches': 10, 'ambiguities' : 'ignore', 'outFormat' : 'json'}
    response = make_map_quest_request_using_cache(site_object, CACHE_DICT, param_dict, BASE_URL)
    mapquest_data = response
    return mapquest_data
    

def format_mapquest_data(mapquest_data):
    '''formats the response from the API for the display list

    

    Parameters
    ----------
    mapquest_data: dict
        the json dict of the info retuened from the API request
    Returns
    -------
    None

    '''
    for i in range(len(mapquest_data['searchResults'])):
        name = mapquest_data["searchResults"][i]["name"]
        category = mapquest_data["searchResults"][i]["fields"]["group_sic_code_name_ext"]
        if not category:
            category = "no category"
        street_address = mapquest_data["searchResults"][i]["fields"]["address"]
        if not street_address:
            street_address = "no address"
        city_name = mapquest_data["searchResults"][i]["fields"]["city"]
        if not city_name:
            city_name = "no city"
        print(f' - {name} ({category}) : {street_address}, {city_name}')
        

def search_function(user_input):
    '''the compilation of all the functions that 
    make the user input produce a diaplay

    converts the input to a display by using multiple other
    functions. done so that the code does not have to be 
    repeated every time. 

    Parameters
    ----------
    user_input: str
        the search term of the user using the program
    Returns
    -------
    list
        the list of media items being diaplayed in the correct format

    '''
    state_url = state_url_dict[user_input.lower()]
    national_site_instance_list = get_sites_for_state(state_url)
    display_list = display_national_sites(national_site_instance_list)
    return display_list

# state_response = make_url_request_using_cache('https://www.nps.gov/state/wy/index.htm', CACHE_DICT)
# print(state_response.text)

if __name__ == "__main__":

    # pass
    state_url_dict = build_state_url_dict()

    user_input = input('Enter the name of a State you would like to search for. Or, enter "exit" to quit. ').lower()
    while True:
        if user_input.lower() == 'exit':
            quit()
        elif user_input.lower() in state_url_dict.keys():
            print("------------------------------------")
            print( " List of National Sites in " + user_input)
            print("------------------------------------")
            display_list = search_function(user_input)
            break
        else:
            print("Enter proper state name. ")
            user_input = input('Enter the name of a State you would like to search for. Or, enter "exit" to quit. ').lower()

    while True:
        user_input = input('Choose the number for detail search or "exit" or "back". ')
        if user_input.lower() == 'exit':
            quit()
        elif user_input.lower() == 'back':
            user_input = input('Enter the name of a State you would like to search for. Or, enter "exit" to quit. ')
            if user_input.lower() == 'exit':
                 quit()
            else:
                display_list = search_function(user_input)



            
        elif user_input.isdigit():
            if int(user_input) <= len(display_list):
                user_input_number = int(user_input) -1
                site_object = display_list[user_input_number]
                mapquest_data = get_nearby_places(site_object)
                print("----------------------------------------")
                print("Places Near " + site_object.name)
                print("----------------------------------------")
                format_mapquest_data(mapquest_data)
                
            elif int(user_input) > len(display_list):
                print('Sorry, that number is out of range. would you like to try again? Search a term, a number in range, or enter "Exit" to exit. ')
        else:
            display_list = search_function(user_input)

            
                


    CACHE_DICT = open_cache()