import os
from datetime import datetime
from http import HTTPStatus
import requests

from dotenv import load_dotenv

from .constants import (
    BASE_OPEN_WEATHER_API_URL,
    DAYTIME_FORMAT,
    DTTM_FORMAT,
)
from .utils import (
    compass_direction,
)

load_dotenv()

API_TOKEN = os.getenv(
    'API_TOKEN',
    'put your OpenWeatherMap token here or set its value in .env file.'
)


def get_openweather_url(city='perm', lon=57.999191, lat=56.274835):
    url = f'{BASE_OPEN_WEATHER_API_URL}?appid={API_TOKEN}&lang=ru&units=metric'
    if city:
        return f'{url}&q={city}'
    elif lon and lat:
        return f'{url}&lat={lat}&lon={lon}'

    raise LookupError(
        'url must contain either city name or lon and lat of location.'
    )


def forecast(city='perm') -> str:
    """Gets and parses weather_api response constructing a bot message."""

    current_dttm = datetime.now()
    current_dttm_str = current_dttm.strftime(format=DTTM_FORMAT)

    try:
        url = get_openweather_url(city)
    except LookupError as args_error:
        return f'ERROR {args_error}'

    response = requests.get(url)

    # in case of weather API bad response:
    if response.status_code != HTTPStatus.OK:
        # ADD LOGGING ERROR
        return f"""
            Нет ответа от {BASE_OPEN_WEATHER_API_URL}
            Статус - {response.status_code}.
        """.replace('    ', '')

    # Parsing weather data
    data = response.json()

    weather_discription = data['weather'][0]['description']
    tempreture = data['main']['temp']
    tempreture_experienced = round(data['main']['feels_like'])

    pressure = data['main']['pressure']
    humidity = data['main']['humidity']
    wind_speed = data['wind']['speed']
    wind_deg = data['wind']['deg']
    wind_direction = compass_direction(wind_deg)

    sunrise = datetime.fromtimestamp(
        data['sys']['sunrise']
    ).strftime(format=DAYTIME_FORMAT)
    sunset = datetime.fromtimestamp(
        data['sys']['sunset']
    ).strftime(format=DAYTIME_FORMAT)

    return f"""
        Погода в -{city.capitalize()}- на {current_dttm_str}:
        {weather_discription.capitalize()} {tempreture}°C; Ощущается как {tempreture_experienced}°C.

        Влажность: {humidity}%
        Ветер: [{wind_direction}] {wind_speed} м/с
        Давление: {pressure} мм.рт.ст.
        Световой день: {sunrise} -- {sunset}.
    """.replace('    ', '')


if __name__ == '__main__':
    result = forecast()
    print(result)
