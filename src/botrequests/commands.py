import requests
import json
from decouple import config

api_key = config("api_key")

headers = {
    'x-rapidapi-host': "hotels4.p.rapidapi.com",
    'x-rapidapi-key': api_key
}


def get_clean_list(hotels: list, min_d: int, max_d: int) -> list:
    """
    Используется для работы с bestdeal, фильтрует отели по параметру расстояния до цетнтра
    :param hotels: список отелей
    :param min_d: минимальное расстояние до центра
    :param max_d: максимальное расстояние до центра
    :return: отфильтрованный список
    """
    result_list = []

    for hotel in hotels:
        hotel_landmark = hotel["landmarks"][0]["distance"]
        hotel_landmark = hotel_landmark[:-3]
        float_hotel_landmark = float(hotel_landmark.replace(',', '.'))

        if float(min_d) < float_hotel_landmark < float(max_d):
            result_list.append(hotel)
    return result_list


def get_destination_id(destination: str) -> str:
    """
    Получение ID города поиска
    :param destination: город поиска
    :return: ID города
    """
    url = "https://hotels4.p.rapidapi.com/locations/search"

    querystring = {"query": str(destination), "locale": "ru_RU"}

    response = requests.request("GET", url, headers=headers, params=querystring)
    result = json.loads(response.text)
    return result['suggestions'][0]['entities'][0]['destinationId']


def hotels_list_by(destination: str, hotels_count: int, checkIn: str, checkOut: str, sort_by: str) -> list:
    """
    Формируется список отелей по зданным параметрам, для комманд lowprice, highprice
    :param destination: ID города
    :param hotels_count: сколько отелей вывести
    :param checkIn: дата заезда
    :param checkOut: дата выезда
    :param sort_by: сортировка, высокая или низкая цена, зависит от изначальной комманды
    :return: список отелей
    """

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

    response = requests.request("GET", url, headers=headers, params=querystring)
    result = json.loads(response.text)
    hotels_list = result["data"]["body"]["searchResults"]["results"]

    return hotels_list


def hotels_list_bestdeal(destination: str, hotels_count: int, checkIn: str, checkOut: str,
                         sort_by: str, min_price: int, max_price: int, min_distance: int, max_distance: int) -> list:
    """
    Формируется список отелей по зданным параметрам, для комманды bestdeal
    :param destination: ID города
    :param hotels_count: сколько отелей вывести
    :param checkIn: дата заезда
    :param checkOut: дата выезда
    :param sort_by: сортировка, сортируется по низкой цене
    :param min_price: минимальная цена
    :param max_price: максимаольная цена
    :param min_distance: мимнимальное расстояние до центра
    :param max_distance: максимальное рассмтояние до центра
    :return: список отелей
    """
    if sort_by == "/bestdeal":
        sort_by = "PRICE"

    if int(hotels_count) > 25:
        hotels_count = "25"
    url = "https://hotels4.p.rapidapi.com/properties/list"

    querystring = {"destinationId": str(destination), "pageNumber": "1", "pageSize": str(hotels_count),
                   "checkIn": checkIn, "checkOut": checkOut, "adults1": "1", "sortOrder": sort_by,
                   "priceMin": str(min_price), "priceMax": str(max_price), "locale": "ru_RU",
                   "currency": "USD"}

    response = requests.request("GET", url, headers=headers, params=querystring)
    result = json.loads(response.text)
    hotels_list = result["data"]["body"]["searchResults"]["results"]

    new_list = get_clean_list(hotels_list, min_distance, max_distance)

    return new_list


def get_photos(hotel_id: str) -> list:
    """
    Получить список фотографий url
    :param hotel_id: ID отеля
    :return:
    """
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

    querystring = {"id": str(hotel_id)}

    response = requests.request("GET", url, headers=headers, params=querystring)
    result = json.loads(response.text)
    photos_list = [x["baseUrl"] for x in result['hotelImages']]
    return photos_list


def form_result_string(hotel: dict) -> str:
    """
    Формируется сообщение с результатом, которое направляется пользователю
    :param hotel: Отель, словарь из списка отелей
    :return: Итоговое сообщение, строка
    """
    result = f"""
  Название отеля: {hotel['name']}
  Адрес: {hotel['address']['locality']}, {hotel['address']['streetAddress']}, {hotel['address']['postalCode']}
  Расстояние до {hotel['landmarks'][0]["label"]} - {hotel['landmarks'][0]["distance"]}
  Цена: {hotel['ratePlan']['price']['current']}
  Ссылка: https://ru.hotels.com/ho{hotel['id']}
  """
    return result
