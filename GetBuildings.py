from collections import defaultdict
import requests
from bs4 import BeautifulSoup
import json
import os
import googlemaps
from dotenv import load_dotenv


def get_coordinates_from_address(address):
    load_dotenv()
    google_api_key = os.getenv("GOOGLE_API_KEY")
    gmaps = googlemaps.Client(key=google_api_key)

    # Geocoding an address
    geocode_result = gmaps.geocode(address)[0]["geometry"]["location"]
    return (geocode_result["lat"], geocode_result["lng"])


def building_code_to_address():
    URL = "https://www.bu.edu/summer/summer-sessions/life-at-bu/campus-resources/building-codes/"

    response = requests.get(URL)
    soup = BeautifulSoup(response.content, "html.parser")

    table = soup.find("table", class_="table-striped")
    # get all trs, skipping header
    rows = table.find_all("tr")[1:]

    buildings = defaultdict(lambda: "")

    for row in rows:
        columns = row.find_all("td")
        abbreviation = columns[0].text.strip()
        description = columns[1].text.strip().replace("\u2019", "'")
        address = (
            columns[2].text.strip().replace("\u2013", "-").replace("\u2019", "'")
            + ", Boston, MA"
        )
        buildings[abbreviation] = (address, get_coordinates_from_address(address))

    # Dump into a JSON
    with open("Semesters/buildings.json", "w") as f:
        json.dump(buildings, f)

    print("Data stored in buildings.json")


building_code_to_address()
