import requests
import json
api_key = "149073f1c0mshd8a1e0d0781eab1p12a20ajsn866b16271dc0"

def get_destination_id(destination):
    url = "https://hotels4.p.rapidapi.com/locations/search"

    querystring = {"query": str(destination), "locale": "ru_RU"}

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': api_key
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    result = json.loads(response.text)
    return result['suggestions'][0]['entities'][0]['destinationId']


def hotels_list_by_lowprice(destination, hotels_count, checkIn, checkOut):
    if hotels_count > 25:
        hotels_count = 25
    url = "https://hotels4.p.rapidapi.com/properties/list"

    querystring = {"destinationId": str(destination), "pageNumber": "1", "pageSize": str(hotels_count),
                   "checkIn": checkIn, "checkOut": checkOut, "adults1": "1", "sortOrder": "PRICE", "locale": "ru_RU",
                   "currency": "USD"}

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': api_key
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    result = json.loads(response.text)
    hotels_list = result["data"]["body"]["searchResults"]["results"]
    return hotels_list


def get_photos(hotel_id):
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

    querystring = {"id": str(hotel_id)}

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': api_key
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    result = json.loads(response.text)
    photos_list = [x["baseUrl"] for x in result['hotelImages']]
    return photos_list
