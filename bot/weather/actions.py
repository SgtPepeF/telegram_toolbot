from http import HTTPStatus
import requests

from settings import (
    DEFAULT_OPENWEATHER_REGION,
)
from .constants import (
    BASE_OPEN_WEATHER_API_URL,
)
from .utils import (
    get_openweather_url,
    compass_direction,
)


def forecast(city=DEFAULT_OPENWEATHER_REGION) -> str:
    """Gets and parses weather_api response constructing a bot message."""

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
    tempreture = round(data['main']['temp'], 1)
    tempreture_experienced = round(data['main']['feels_like'])

    pressure = data['main']['pressure']
    pressure = round(pressure * 0.75006)  # to turn hPa into mmHg
    humidity = data['main']['humidity']
    wind_speed = data['wind']['speed']
    wind_deg = data['wind']['deg']
    wind_direction = compass_direction(wind_deg)

    return f"""
        Погода в -{city.capitalize()}-
        {weather_discription.capitalize()} {tempreture}°C; Ощущается как {tempreture_experienced}°C.

        Влажность: {humidity}%
        Ветер: [{wind_direction}] {wind_speed} м/с
        Давление: {pressure} мм.рт.ст.
    """.replace('    ', '')


if __name__ == '__main__':
    result = forecast()
    print(result)
