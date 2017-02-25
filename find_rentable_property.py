import json
import urllib
from pip._vendor import requests

# API key for google maps
from google_maps_password import GMAPS_PASSWORD

# A per week price limit on rentable properties
PRICE_LIMIT_PER_WEEK = 500

WORK = "Sydney NSW 2000"
SCHOOL = "Sydney NSW 2109"

def get_locations():
    # Grab all rental properties within price_limit_per_week and return them
    return []


'''Given a valid address_name this method finds the location's place_id
'''
def get_place_id(address_name):
    # Convert address_name into a placeID. No error checking, assuming address_name corresponds with a google placeID



def find_nearest_house():
    # Pull houses from rent site
    # loop through houses
        # Get individual house placeID
        # compute distance from work and school
    #output property closest to work and school



if __name__ == "__main__":
    # Instantiate variables and run code
    WORK = get_place_id(WORK)
    SCHOOL = get_place_id(SCHOOL)
    find_nearest_house()