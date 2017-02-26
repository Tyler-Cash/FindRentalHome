import json
import urllib
import re
import time
import functools
import requests
import sys
from house import House, create_house
from bs4 import BeautifulSoup
# API key for google maps
from google_maps_password import GMAPS_PASSWORD

# A per week price limit on rentable properties
PRICE_LIMIT_PER_WEEK = 500
# Location of work and school
WORK = "Sydney NSW 2000"
SCHOOL = "Sydney NSW 2109"
# WORK_PRIORITY prioritizes properties depending on how close they are to either, school or work.
# 0 - - - - .5 - - - - 1
#School    Even       Work
WORK_PRIORITY = .8


def get_locations_from_realestatecomau(pets_allowed):
    # Grab all rental properties within price_limit_per_week and return them
    all_houses = []
    total_pages = 20
    page_number = 1
    # Total pages is + 1 since iterator starts at 1, not 0
    while page_number < total_pages + 1:
        # Acquires page to be scraped
        property_search = "http://www.realestate.com.au/rent/between-0-" + str(
            PRICE_LIMIT_PER_WEEK) + "-in-blacktown%2c+nsw+2148%3b+parramatta+-+greater+region%2c+nsw%3b+newtown%2c+nsw+2042%3b+chullora%2c+nsw+2190%3b+wetherill+park%2c+nsw+2164%3b+baulkham+hills%2c+nsw+2153%3b+oxley+park%2c+nsw+2760%3b+mount+druitt%2c+nsw+2770%3b+penrith+-+greater+region%2c+nsw%3b+sydney+cbd%2c+nsw%3b+sydney%2c+nsw+2000%3b+strathfield%2c+nsw+2135%3b+surry+hills%2c+nsw+2010%3b+hurstville%2c+nsw+2220%3b+padstow%2c+nsw+2211%3b/list-" + str(
            page_number) + "?activeSort=price-asc"
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
                    cost_per_week = "No price listed"
            else:
                cost_per_week = "No price listed"

            extracted_house = create_house(address, cost_per_week, url)
            all_houses.append(extracted_house)
        # Sleeps for 5 seconds after requesting to reduce load
        time.sleep(.2)
        page_number += 1

    return all_houses


'''Given a valid address_name this method finds the location's place_id
'''


def get_place_id(address_name):
    # Convert address_name into a placeID. No error checking, assuming address_name corresponds with a google placeID
    address_name = urllib.parse.quote(address_name)
    response = None
    while response is None or response['status'] == "OVER_QUERY_LIMIT":
        response = requests.get(
            "https://maps.googleapis.com/maps/api/geocode/json?address=" + address_name + "&key=" + GMAPS_PASSWORD)
        response = json.loads(response.text)
        # Returns None so that all of the properties already found can be sorted correctly.
        if response['status'] == "OVER_QUERY_LIMIT":
            return None

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
    if response["status"] == "ZERO_RESULTS" or response["status"] == "NOT_FOUND":
        return 9999999
    return response["routes"][0]["legs"][0]["duration"]["value"]


def compare_houses(house_one, house_two):
    # This returns whatever one is closer to work, whilst also ensuring it's reasonably close to school
    return (house_one.distance_to_work / WORK_PRIORITY + house_one.distance_to_school) - \
           (house_two.distance_to_work / WORK_PRIORITY + house_two.distance_to_school)


def find_nearest_house():
    # Pull houses from rent site
    print("Pulling all houses from http://realestate.com.au")
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
    closest_to_school = sorted(rental_properties, key=functools.cmp_to_key(compare_houses))
    print_all_properties(closest_to_school)


def print_all_properties(all_properties):
    for property in all_properties:
        print("________________\naddress: " + property.address + "\ncost p/w: " + str(
            property.cost_per_week) + "\nurl: " + property.url + "\nTime to school: ", end='')

        invalid_property = False
        if property.distance_to_school == 9999999:
            invalid_property = True

        time_to_school_minutes = property.distance_to_school / 60
        time_to_school_hours = int(time_to_school_minutes / 60)
        time_to_school_minutes = int(time_to_school_minutes % 60)

        if time_to_school_hours is not 0 and not invalid_property:
            print(str(time_to_school_hours) + ":" + str(time_to_school_minutes).zfill(2)  + " hours")
        elif invalid_property:
            print("Couldn't find property")
        else:
            print(str(time_to_school_minutes).zfill(2)  + " minutes")

        print("Time to work: ", end='')

        time_to_work_minutes = property.distance_to_work / 60
        time_to_work_hours = int(time_to_work_minutes / 60)
        time_to_work_minutes = int(time_to_work_minutes % 60)

        if time_to_work_hours is not 0 and not invalid_property:
            print(str(time_to_work_hours) + ":" + str(time_to_work_minutes).zfill(2)  + " hours")
        elif invalid_property:
            print("Couldn't find property")
        else:
            print(str(time_to_work_minutes).zfill(2)  + " minutes")


if __name__ == "__main__":
    # Instantiate variables and run code
    WORK = get_place_id(WORK)
    SCHOOL = get_place_id(SCHOOL)
    find_nearest_house()
