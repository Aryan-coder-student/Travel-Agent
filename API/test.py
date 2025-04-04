import requests
BASE_URL = "http://127.0.0.1:8000"
def test_flight_details():
    params = {
        "from_location_ID": "DEL",
        "to_location_ID": "BHO",
        "departure_date": "2025-04-05",
    }
    response = requests.get(f"{BASE_URL}/flights", params=params)
    print("Flight Details:", response.json())


def test_train_details():
    params = {
        "departure_code": "JBP",
        "departure_name": "Jabalpur",
        "destination_code": "BPL",
        "destination_name": "Bhopal Jn",
        "journey_date": "7-4-2025"
    }
    response = requests.get(f"{BASE_URL}/train-details", params=params)
    print("Train Details:", response.text[:500]) 


def test_hotel_details(): 
    payload = {
        "stay_city_and_type": "Hotels in Goa",
        "check_in_date": "2025-04-10",
        "check_out_date": "2025-04-15",
        "num_adults": 2,
        "min_price": 1000,
        "max_price": 5000,
        "num_children": 0,
        "children_ages": [],
        "page": 1
    }

    response = requests.post(f"{BASE_URL}/hotels", json=payload)
    print("Hotel Details:", response.json())


if __name__ == "__main__":
    pass
    test_flight_details()
    # test_train_details()
    # test_hotel_details()
