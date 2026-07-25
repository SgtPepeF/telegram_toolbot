import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()

DEBUG_MODE = os.getenv('DEBUG_MODE') == 'True'

TELEGRAM_API_TOKEN = os.getenv(
    'TELEGRAM_API_TOKEN',
    'put your telegram token here or set its value in .env file'
)
ADMIN_TELEGRAM_ID = int(os.getenv('ADMIN_TELEGRAM_ID'))

hours, minutes = [
    int(time_value)
    for time_value
    in os.getenv('ADMIN_TIMEZONE').split(':')
]
ADMIN_TIMEZONE = timedelta(hours=hours, minutes=minutes)

OPEN_WEATHER_API_TOKEN = os.getenv(
    'OPEN_WEATHER_API_TOKEN',
    'put your OpenWeatherMap token here '
)
DEFAULT_OPENWEATHER_REGION = os.getenv(
    'ADMIN_OPENWEATHER_REGION',
    'moscow'  # Write your default region here or set its value in .env file.
)

# used for script 'db_creation.py' to work.
# That's how App knows, where to look for models.py files.
REGISTERED_APPS = (
    'database',
    'scheduler',
    'weather',
)
