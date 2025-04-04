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
from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()
SERP_API_KEY = os.getenv("SERP_API_KEY")
ANT_SCRAPY_API_KEY = os.getenv("ANT_SCRAPY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHROMA_DB_PATH = "./chroma_db"
embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


# api_key = os.getenv("AVIATIONSTACK_API_KEY")
# url = "http://api.aviationstack.com/v1/airports"
# params = {"access_key": api_key, "search": city}
# response = requests.get(url, params=params).json()

# if response.get("data"):
#     return response["data"][0]["iata_code"]





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

def get_station_code(city):
    return station_code_lookup.get(city, None)

def get_iata_code(city):
    return iata_code_lookup.get(city, None)


llm = ChatGroq(model_name="llama-3.3-70b-versatile", api_key=GROQ_API_KEY)
chroma_client = Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embedding_function, collection_name="travel_data")

retriever = chroma_client.as_retriever()
def get_iata_code(city):
    return iata_code_lookup.get(city, None)

def fetch_data(endpoint, params=None):

    base_url = "http://localhost:8000"  
    response = requests.get(f"{base_url}{endpoint}", params=params)
    return response.json()

def get_travel_data(user_input):
    
    from_iata = get_iata_code(user_input["from_city"])
    to_iata = get_iata_code(user_input["to_city"])
    
    from_station_code = get_station_code(user_input["from_city"])
    to_station_code = get_station_code(user_input["to_city"])

    flight_data = fetch_data("/flights", {
        "from_location_ID": from_iata,
        "to_location_ID": to_iata,
        "departure_date": user_input["departure_date"],
    })


    hotel_data = fetch_data("/hotels", {
        "stay_city_and_type": user_input["to_city"] + " hotels",
        "check_in_date": user_input["departure_date"],
        "check_out_date": user_input["return_date"],
        "num_adults": user_input["num_adults"],
        "min_price": user_input["min_price"],
        "max_price": user_input["max_price"],
        "num_children": user_input["num_children"],
        "children_ages": user_input["children_ages"],
        "page": 3
    })

    activities_data = fetch_data("/activities", {
        "activity_query": "Restaurants in " + user_input["to_city"],
        "destination_city": user_input["to_city"],
        "num_pages": 3
    })

    train_data = fetch_data("/train-details", {
        "departure_code": from_station_code,
        "departure_name": user_input["from_city"],
        "destination_code": to_station_code ,
        "destination_name": user_input["to_city"],
        "journey_date": user_input["departure_date"]
    })

    tourist_places = fetch_data("/tourist-places", {
        "place_type": "tourist attractions",
        "destination_city": user_input["to_city"],
        "num_pages": 3
    })

    return flight_data, hotel_data, activities_data, train_data, tourist_places




def store_in_chromadb(data_dict):
    """Convert travel data to documents and store them in ChromaDB"""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    for category, data in data_dict.items():
        if not data:
            continue
        text = f"Category: {category}\n{str(data)}"
        docs = [Document(page_content=chunk) for chunk in text_splitter.split_text(text)]
        chroma_client.add_documents(docs)



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

    Output day-wise itinerary including flights, hotels, Restaurant details , recommended tourist places , share their location link also or co-ordinates of the map.
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
