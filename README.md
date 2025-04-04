# Travel Planning API
https://github.com/user-attachments/assets/d8651b46-3ddd-4fc4-8498-74f71c539d06

A comprehensive backend service that helps users plan their travel by fetching flight information, hotel details, local activities, tourist attractions, and train details, then generating personalized travel itineraries.

## Overview

This API integrates multiple data sources including Google Flights, Google Hotels, Google Local, and train information to create detailed travel plans. It uses RAG (Retrieval-Augmented Generation) with LLM to generate personalized itineraries based on user preferences and constraints.

## Tech Stack

- **FastAPI**: Web framework for API endpoints
- **LangChain**: Framework for LLM applications
- **ChromaDB**: Vector database for storing travel data
- **Groq**: LLM provider (using llama-3.3-70b-versatile model)
- **HuggingFace Embeddings**: Sentence embeddings for semantic search
- **SerpAPI**: For fetching Google search results
- **ScrapingAnt**: For web scraping train information

## Workflow

1. **Data Collection**: The API collects travel data from multiple sources:
   - Flight details from Google Flights
   - Hotel options from Google Hotels
   - Local activities and restaurants from Google Local
   - Tourist attractions from Google Local
   - Train details by scraping RailYatri




2. **Data Storage**: All collected travel data is:
   - Chunked using RecursiveCharacterTextSplitter
   - Embedded using HuggingFace embeddings
   - Stored in ChromaDB for retrieval

3. **Itinerary Generation**: Using the stored data, the API:
   - Retrieves relevant information based on user query
   - Generates a detailed day-wise itinerary using the LLM
   - Includes recommendations within the user's budget and preferences

## API Endpoints

### 1. Generate Complete Itinerary
```
POST /generate-itinerary
```
Generate a comprehensive travel plan based on user preferences.

**Request Body**:
```json
{
  "from_city": "Mumbai",
  "to_city": "Jaipur",
  "departure_date": "2025-05-15",
  "return_date": "2025-05-20",
  "num_adults": 2,
  "num_children": 1,
  "children_ages": [8],
  "min_price": 2000,
  "max_price": 8000,
  "budget": 50000,
  "days": 5,
  "from_station": "CSTM",
  "to_station": "JP"
}
```

**Response**: Returns a complete itinerary with day-wise plans, travel recommendations, and cost estimates.

### 2. Flight Information
```
GET /flights
```
Get flight details between two locations.

**Query Parameters**:
- `from_location_ID`: IATA code for departure airport
- `to_location_ID`: IATA code for arrival airport
- `departure_date`: Date of travel (YYYY-MM-DD)

### 3. Hotel Details
```
POST /hotels
```
Get hotel options based on location and preferences.

**Request Body**:
```json
{
  "stay_city_and_type": "Jaipur hotels",
  "check_in_date": "2025-05-15",
  "check_out_date": "2025-05-20",
  "num_adults": 2,
  "min_price": 2000,
  "max_price": 8000,
  "num_children": 1,
  "children_ages": [8],
  "page": 3
}
```

### 4. Local Activities
```
GET /activities
```
Get information about local activities in the destination city.

**Query Parameters**:
- `activity_query`: Type of activity (e.g., "Restaurants")
- `destination_city`: City name
- `num_pages`: Number of result pages to fetch (default: 3)

### 5. Tourist Places
```
GET /tourist-places
```
Get information about tourist attractions in the destination city.

**Query Parameters**:
- `place_type`: Type of tourist place (e.g., "tourist attractions")
- `destination_city`: City name
- `num_pages`: Number of result pages to fetch (default: 3)

### 6. Train Details
```
GET /train-details
```
Get train information between two stations.

**Query Parameters**:
- `departure_code`: Station code for departure
- `departure_name`: Name of departure station
- `destination_code`: Station code for arrival
- `destination_name`: Name of arrival station
- `journey_date`: Date of journey (YYYY-MM-DD)

## Setup and Configuration

### Environment Variables
The application requires the following environment variables:
- `SERP_API_KEY`: API key for SerpAPI
- `ANT_SCRAPY_API_KEY`: API key for ScrapingAnt
- `GROQ_API_KEY`: API key for Groq
- `CHROMA_DB_PATH`: Path for ChromaDB (default: "./chroma_db")

### Running the Application
```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --host 0.0.0.0 --port 8080
```

## Helper Functions

The API includes several helper functions:
- City code lookups for IATA and railway station codes
- Data fetching utilities
- ChromaDB storage functions
- Travel data collection functions

## Note on Data Usage

This API relies on external data sources. Please be aware of the rate limits and terms of service for:
- SerpAPI
- ScrapingAnt
- Groq

## Future Improvements

Potential enhancements for the API:
- Add caching to reduce API calls
- Implement user authentication
- Add more travel options (buses, car rentals)
- Include weather forecasts for the destination
- Add budget optimization features
