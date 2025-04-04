import os
import requests
import chromadb
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from fastapi import FastAPI, Request, Query
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from serpapi import GoogleSearch
from langchain_community.document_loaders import ScrapingAntLoader
import uvicorn

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
load_dotenv()
SERP_API_KEY = os.getenv("SERP_API_KEY")
ANT_SCRAPY_API_KEY = os.getenv("ANT_SCRAPY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHROMA_DB_PATH = "./chroma_db"

# Initialize embeddings and ChromaDB
embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
chroma_client = Chroma(persist_directory=CHROMA_DB_PATH, 
                      embedding_function=embedding_function, 
                      collection_name="travel_data")
retriever = chroma_client.as_retriever()

# Initialize LLM
llm = ChatGroq(model_name="llama-3.3-70b-versatile", api_key=GROQ_API_KEY)

# City code lookups
iata_code_lookup = {
    "New Delhi": "DEL",
    "Mumbai": "BOM",
    "Bangalore": "BLR",
    "Hyderabad": "HYD",
    "Chennai": "MAA",
    "Kolkata": "CCU",
    "Pune": "PNQ",
    "Ahmedabad": "AMD",
    "Jaipur": "JAI",
    "Bhopal": "BPL",
    "Lucknow": "LKO",
    "Goa": "GOI",
    "Patna": "PAT",
    "Guwahati": "GAU",
    "Nagpur": "NAG",
    "Visakhapatnam": "VTZ",
    "Coimbatore": "CJB",
    "Thiruvananthapuram": "TRV",
    "Indore": "IDR",
    "Varanasi": "VNS"
}

station_code_lookup = {
    "New Delhi": "NDLS",
    "Mumbai": "CSTM",   
    "Bangalore": "SBC",
    "Hyderabad": "HYB",
    "Chennai": "MAS",
    "Kolkata": "HWH",   
    "Pune": "PUNE",
    "Ahmedabad": "ADI",
    "Jaipur": "JP",
    "Bhopal": "BPL",
    "Lucknow": "LKO",
    "Goa": "MAO",        
    "Patna": "PNBE",
    "Guwahati": "GHY",
    "Nagpur": "NGP",
    "Visakhapatnam": "VSKP",
    "Coimbatore": "CBE",
    "Thiruvananthapuram": "TVC",
    "Indore": "INDB",
    "Varanasi": "BSB"
}

# Helper functions
def get_station_code(city):
    return station_code_lookup.get(city, None)

def get_iata_code(city):
    return iata_code_lookup.get(city, None)

def fetch_data(endpoint, params=None):
    base_url = "http://localhost:8000"  # Using the same app now
    response = requests.get(f"{base_url}{endpoint}", params=params)
    return response.json()

# API Endpoints
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
        "api_key": SERP_API_KEY,
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return results

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
            "api_key": SERP_API_KEY,
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
            "api_key": SERP_API_KEY,
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
            "api_key": SERP_API_KEY,
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
        api_key=ANT_SCRAPY_API_KEY,
        continue_on_failure=True
    )
    docs = loader.load()
    return {"page_content": docs[0].page_content if docs else ""}

# RAG functionality
def store_in_chromadb(data_dict):
    """Convert travel data to documents and store them in ChromaDB"""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    for category, data in data_dict.items():
        if not data:
            continue
        text = f"Category: {category}\n{str(data)}"
        docs = [Document(page_content=chunk) for chunk in text_splitter.split_text(text)]
        chroma_client.add_documents(docs)

def get_travel_data(user_input):
    from_iata = get_iata_code(user_input["from_city"])
    to_iata = get_iata_code(user_input["to_city"])
    
    from_station_code = get_station_code(user_input["from_city"])
    to_station_code = get_station_code(user_input["to_city"])

    flight_data = get_flight_details(
        from_location_ID=from_iata,
        to_location_ID=to_iata,
        departure_date=user_input["departure_date"]
    )

    hotel_data = get_hotel_details(HotelRequest(
        stay_city_and_type=user_input["to_city"] + " hotels",
        check_in_date=user_input["departure_date"],
        check_out_date=user_input["return_date"],
        num_adults=user_input["num_adults"],
        min_price=user_input["min_price"],
        max_price=user_input["max_price"],
        num_children=user_input["num_children"],
        children_ages=user_input["children_ages"],
        page=3
    ))

    activities_data = get_local_activities(
        activity_query="Restaurants in " + user_input["to_city"],
        destination_city=user_input["to_city"],
        num_pages=3
    )

    train_data = get_train_details(
        departure_code=from_station_code,
        departure_name=user_input["from_city"],
        destination_code=to_station_code,
        destination_name=user_input["to_city"],
        journey_date=user_input["departure_date"]
    )

    tourist_places = get_tourist_places(
        place_type="tourist attractions",
        destination_city=user_input["to_city"],
        num_pages=3
    )

    return flight_data, hotel_data, activities_data, train_data, tourist_places

def generate_travel_plan(user_input):
    """Generate a personalized travel plan using LLM and retrieved travel data"""
    flight_data, hotel_data, activities_data, train_data, tourist_places = get_travel_data(user_input)
    store_in_chromadb({
        "Flights": flight_data,
        "Hotels": hotel_data,
        "Activities": activities_data,
        "Trains": train_data,
        "Tourist Places": tourist_places
    })
    
    prompt_template = """
    You are an AI Travel Assistant. Based on the retrieved travel details and user constraints, create a detailed travel plan.

    User Constraints:
    - Budget: INR {budget}
    - Duration: {days} days
    - Destination: {to_city}
    - current city: {from_city}

    Travel Data:
    {context}

    Output day-wise itinerary including flights, hotels, Restaurant details, recommended tourist places, share their location link also or co-ordinates of the map.
    Also provide sources for each recommendation and available flights from the current city to the destination city.
    """

    qa_chain = RetrievalQA.from_chain_type(llm, retriever=retriever)
    response = qa_chain.run(prompt_template.format(
        budget=user_input["budget"],
        days=user_input["days"],
        to_city=user_input["to_city"],
        from_city=user_input["from_city"],
        context="{context}"  
    ))

    return response


class TravelRequest(BaseModel):
    from_city: str
    to_city: str
    departure_date: str
    return_date: str
    num_adults: int
    num_children: int
    children_ages: list
    min_price: int
    max_price: int
    budget: int
    days: int
    from_station: str
    to_station: str

@app.post("/generate-itinerary")
def generate_itinerary(request: TravelRequest):
    result = generate_travel_plan(request.model_dump())
    return {"itinerary": result}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)