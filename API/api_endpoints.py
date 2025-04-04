from fastapi import FastAPI, Query
from typing import List, Optional
from pydantic import BaseModel
from serpapi import GoogleSearch
from langchain_community.document_loaders import ScrapingAntLoader
import dotenv
import os


dotenv.load_dotenv()
serp_api = os.getenv("SERP_API_KEY")
ant_scrap = os.getenv("ANT_SCRAPY_API_KEY")

app = FastAPI()

class HotelRequest(BaseModel):
    stay_city_and_type: str
    check_in_date: str
    check_out_date: str
    num_adults: int
    min_price: int
    max_price: int
    num_children: int = 0
    children_ages: List[int] = [0]
    page: int = 3

@app.get("/flights")
def get_flight_details(from_location_ID: str, to_location_ID: str, departure_date: str):
    params = {
        "engine": "google_flights",
        "hl": "en",
        "gl": "us",
        "departure_id": from_location_ID,
        "arrival_id": to_location_ID,
        "outbound_date": departure_date,
        "currency": "INR",
        "type": 2,
        "api_key": serp_api,
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return results

@app.post("/hotels")
def get_hotel_details(request: HotelRequest):
    all_properties = []
    for _ in range(3):
        params = {
            "engine": "google_hotels",
            "hl": "en",
            "gl": "us",
            "q": request.stay_city_and_type,
            "check_in_date": request.check_in_date,
            "check_out_date": request.check_out_date,
            "adults": request.num_adults,
            "children": request.num_children,
            "children_ages": request.children_ages,
            "min_price": request.min_price,
            "max_price": request.max_price,
            "currency": "INR",
            "api_key": serp_api,
            "start": request.page * 10,
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        properties = results.get("properties", [])
        if not properties:
            break
        all_properties.extend(properties)
    return all_properties

@app.get("/activities")
def get_local_activities(activity_query: str, destination_city: str, num_pages: int = 3):
    all_places = []
    for page in range(num_pages):
        params = {
            "api_key": serp_api,
            "engine": "google_local",
            "google_domain": "google.com",
            "q": f"{activity_query} in {destination_city}",
            "hl": "en",
            "gl": "us",
            "start": page * 20,
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        places = results.get("local_results", [])
        if not places:
            break
        all_places.extend(places)
    return all_places

@app.get("/tourist-places")
def get_tourist_places(place_type: str, destination_city: str, num_pages: int = 3):
    all_places = []
    for page in range(num_pages):
        params = {
            "api_key": serp_api,
            "engine": "google_local",
            "google_domain": "google.com",
            "q": f"{place_type} in {destination_city}",
            "hl": "en",
            "gl": "us",
            "start": page * 20,
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        places = results.get("local_results", [])
        if not places:
            break
        all_places.extend(places)
    return all_places

@app.get("/train-details")
def get_train_details(departure_code: str, departure_name: str,
                      destination_code: str, destination_name: str,
                      journey_date: str):
    base_url = (
        "https://www.railyatri.in/trains-between-stations-v2"
        f"?from_code={departure_code}"
        f"&from_name={departure_name.upper().replace(' ', '%20')}"
        f"&to_code={destination_code}"
        f"&to_name={destination_name.upper().replace(' ', '%20')}"
        f"&journey_date={journey_date}"
        f"&user_id=-1743734480&user_token=&device_type_id=6"
        f"&src=ttb_landing&from_sta_code={departure_code}&to_sta_code={destination_code}"
    )
    loader = ScrapingAntLoader(
        [base_url],
        api_key=ant_scrap,
        continue_on_failure=True
    )
    docs = loader.load()
    return {"page_content": docs[0].page_content if docs else ""}
