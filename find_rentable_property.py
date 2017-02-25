import json
import urllib

import re

import time
from lxml import html
import requests
from house import House, create_house
from bs4 import BeautifulSoup

# API key for google maps
from google_maps_password import GMAPS_PASSWORD

# A per week price limit on rentable properties
PRICE_LIMIT_PER_WEEK = 500

WORK = "Sydney NSW 2000"
SCHOOL = "Sydney NSW 2109"


def get_locations_from_realestatecomau(pets_allowed):
    # Grab all rental properties within price_limit_per_week and return them
    all_houses = []
    total_pages = 20
    page_number = 1
    # Total pages is + 1 since iterator starts at 1, not 0
    while page_number < total_pages + 1:
        # Acquires page to be scraped
        property_search = "http://www.realestate.com.au/rent/property-unitblock-villa-townhouse-unit+apartment-house-between-0-" + str(
            PRICE_LIMIT_PER_WEEK) + "-in-nsw/list-" + str(page_number) + "?activeSort=price-asc"
        if pets_allowed:
            property_search += "&misc=pets-allowed"

        # Grabs page
        page = requests.get(property_search)
        soup = BeautifulSoup(page.text, "lxml")

        # Scapes total pages of properties available
        if page_number is 1:
            total_results = soup.find("div", {"class": "resultsInfo"})
            total_results = total_results.encode("utf-8")
            total_results = total_results.decode("utf-8")
            total_pages = int(re.findall("\d{3,}", total_results)[0])
            if total_pages % 20 is not 0:
                total_pages = int(total_pages / 20 + 1)
            else:
                total_pages /= 20


        # Scrapes each house info section
        available_houses = soup.find_all("article", {"class": "resultBody"})
        # Scrapes all info for each house
        for house in available_houses:
            url = "http://www.realestate.com.au" + house.find("a", {"class": "detailsButton"}).get("href")

            address = house.find("a", {"rel": "listingName"}).contents[0]

            cost_per_week = house.find("p", {"class": "priceText"})
            if cost_per_week is not None:
                cost_per_week = cost_per_week.encode("utf-8")
                cost_per_week = cost_per_week.decode("utf-8")
                cost_per_week = re.findall("[$]\d{0,4}", cost_per_week)
                if len(cost_per_week) is 1:
                    cost_per_week = cost_per_week[0]
                else:
                    cost_per_week = 9999
            else:
                cost_per_week = 9999

            extracted_house = create_house(address, cost_per_week, url)
            all_houses.append(extracted_house)
            print("________________\nhouse number: " + str(len(all_houses)) + "\naddress: " + address + "\ncost p/w: " + str(cost_per_week) + "\n url: " + url)


        # Sleeps for 5 seconds after requesting to reduce load
        time.sleep(1)
        page_number += 1

    return all_houses


'''Given a valid address_name this method finds the location's place_id
'''
def get_place_id(address_name):
    # Convert address_name into a placeID. No error checking, assuming address_name corresponds with a google placeID
    address_name = urllib.parse.quote(address_name)
    response = requests.get(
        "https://maps.googleapis.com/maps/api/geocode/json?address=" + address_name + "&key=" + GMAPS_PASSWORD)
    response = json.loads(response.text)
    # Extracts placeID of address_name from JSON response
    place_id = response['results'][0]['place_id']
    return place_id



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