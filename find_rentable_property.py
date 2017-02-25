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
            total_pages = re.findall("\d{1,}", total_results)
            total_pages = int(total_pages[len(total_pages) - 1])
            if total_pages % 20 is not 0:
                total_pages = int(total_pages / 20 + 1)
            else:
                total_pages /= 20

        # Scrapes each house info section
        available_houses = soup.find_all("article", {"class": "resultBody"})
        # Scrapes all info for each house
        for house in available_houses:
            url = "http://www.realestate.com.au" + house.find("a", {"class": "detailsButton"}).get("href")

            address = str(house.find("a", {"rel": "listingName"}).contents[0])

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
    # Captures a place google can't find
    if response['status'] == "ZERO_RESULTS":
        return None
    # Extracts placeID of address_name from JSON response
    place_id = response['results'][0]['place_id']
    return place_id


def time_taken_transit(origin, destination, time):
    response = requests.get(
        "https://maps.googleapis.com/maps/api/directions/json?&mode=transit&arrival_time=" +
        str(time) + "&origin=place_id:" + origin + "&destination=place_id:" + destination + "&key=" + GMAPS_PASSWORD)
    response = json.loads(response.text)
    if response["status"] == "ZERO_RESULTS":
        return 9999999
    return response["routes"][0]["legs"][0]["duration"]["value"]


def find_nearest_house():
    # Pull houses from rent site
    print("pulling all houses")
    rental_properties = get_locations_from_realestatecomau(True)

    # loop through houses
    print("Calculating distance between properties and school/work")

    for property in rental_properties:
        # Get individual house placeID
        house = get_place_id(property.address)

        if house is None:
            continue

        # compute distance from rental property to work
        property.distance_to_work = time_taken_transit(house, WORK, 1488146400)
        # compute distance from rental property to school
        property.distance_to_school = time_taken_transit(house, SCHOOL, 1488146400)

    # output property closest to school
    print("___________________________________________________________________\nOutput closest to school:\n")
    closest_to_school = sorted(rental_properties, key=lambda x: x.distance_to_school)
    for property in closest_to_school:
        print("________________\naddress: " + property.address + "\ncost p/w: " + str(
            property.cost_per_week) + "\nurl: " + property.url + "\nTime to school: " + str(
            property.distance_to_school / 60) + " minutes\nTime to work:" + str(
            property.distance_to_work / 60) + " minutes")

    # output property closest to work
    print("___________________________________________________________________\nOutput closest to work:\n")
    closest_to_school = sorted(rental_properties, key=lambda x: x.distance_to_work)
    for property in closest_to_school:
        print("________________\naddress: " + property.address + "\ncost p/w: " + str(
            property.cost_per_week) + "\nurl: " + property.url + "\nTime to school: " + str(
            property.distance_to_school / 60) + " minutes\nTime to work:" + str(
            property.distance_to_work / 60) + " minutes")


if __name__ == "__main__":
    # Instantiate variables and run code
    WORK = get_place_id(WORK)
    SCHOOL = get_place_id(SCHOOL)
    find_nearest_house()
