import requests
import json
from decouple import config

api_key = config("api_key")


def get_clean_list(hotels, min_d, max_d):
    result_list = []

    for hotel in hotels:
        hotel_landmark = hotel["landmarks"][0]["distance"]
        hotel_landmark = hotel_landmark[:-3]
        float_hotel_landmark = float(hotel_landmark.replace(',', '.'))

        if float(min_d) < float_hotel_landmark < float(max_d):
            result_list.append(hotel)
    print(result_list)
    return result_list


# def best_deal_sort(hotel):
#     return hotel['ratePlan']['price']['exactCurrent']


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


def hotels_list_by(destination, hotels_count, checkIn, checkOut, sort_by):
    hotels_to_result = int(hotels_count)
    if sort_by == "/lowprice":
        sort_by = "PRICE"
    elif sort_by == "/highprice":
        sort_by = "PRICE_HIGHEST_FIRST"

    if int(hotels_count) > 25:
        hotels_count = "25"
    url = "https://hotels4.p.rapidapi.com/properties/list"

    querystring = {"destinationId": str(destination), "pageNumber": "1", "pageSize": str(hotels_count),
                   "checkIn": checkIn, "checkOut": checkOut, "adults1": "1", "sortOrder": sort_by, "locale": "ru_RU",
                   "currency": "USD"}
    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': api_key
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    result = json.loads(response.text)
    hotels_list = result["data"]["body"]["searchResults"]["results"]

    return hotels_list


def hotels_list_bestdeal(destination, hotels_count, checkIn, checkOut,
                         sort_by, min_price, max_price, min_distance, max_distance):
    hotels_to_result = int(hotels_count)
    if sort_by == "/bestdeal":
        sort_by = "PRICE"

    if int(hotels_count) > 25:
        hotels_count = "25"
    url = "https://hotels4.p.rapidapi.com/properties/list"

    querystring = {"destinationId": str(destination), "pageNumber": "1", "pageSize": str(hotels_count),
                   "checkIn": checkIn, "checkOut": checkOut, "adults1": "1", "sortOrder": sort_by,
                   "priceMin": str(min_price), "priceMax": str(max_price), "locale": "ru_RU",
                   "currency": "USD"}
    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': api_key
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    result = json.loads(response.text)
    hotels_list = result["data"]["body"]["searchResults"]["results"]

    new_list = get_clean_list(hotels_list, min_distance, max_distance)
    # sorted_list = sorted(new_list, key=best_deal_sort)
    # result = []
    # for index in range(hotels_to_result):
    #     result.append(sorted_list[index])

    return new_list


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


def form_result_string(hotel):
    result = f"""
  Название отеля: {hotel['name']}
  Адрес: {hotel['address']['locality']}, {hotel['address']['streetAddress']}, {hotel['address']['postalCode']}
  Расстояние до {hotel['landmarks'][0]["label"]} - {hotel['landmarks'][0]["distance"]}
  Цена: {hotel['ratePlan']['price']['current']}
  Ссылка: https://ru.hotels.com/ho{hotel['id']}
  """
    return result


def form_history(history_list):
    result = f"""
          История запросов:\n
          """
    for item in history_list:
        history_string = f"Тип: {item[0]} Город: {item[1]} Дата заезда: {item[3]} Дата выезда: {item[4]}\n"
        result += history_string

    return result
