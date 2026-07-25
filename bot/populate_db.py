from datetime import datetime

from database import SessionLocal
from database.queries import create_user, get_user
from scheduler.queries import (
    create_task,
    create_user_timezone,
    get_user_timezone,
)
from weather.queries import create_location

from settings import (
    ADMIN_TELEGRAM_ID,
    ADMIN_TIMEZONE,
    DEFAULT_OPENWEATHER_REGION,
)

REGULAR_TASK_TIME_FORMAT = '%H:%M'

session = SessionLocal()

# create admin user
try:
    create_user(
        user_kwargs={
            'user_id': ADMIN_TELEGRAM_ID,
        }
    )
except ValueError as user_exists:
    print(user_exists)
except KeyError as wrong_params:
    print(wrong_params)

user = get_user({'user_id': ADMIN_TELEGRAM_ID})

# determine admin user region
# create admin user
try:
    create_location(
        location_kwargs={
            'user_id': ADMIN_TELEGRAM_ID,
            'location': DEFAULT_OPENWEATHER_REGION,
        }
    )
except ValueError as location_exists:
    print(location_exists)
except KeyError as wrong_params:
    print(wrong_params)


# determine admin user region
try:
    create_location(
        location_kwargs={
            'user_id': ADMIN_TELEGRAM_ID,
            'location': DEFAULT_OPENWEATHER_REGION,
        }
    )
except ValueError as location_exists:
    print(location_exists)
except KeyError as wrong_params:
    print(wrong_params)


# creating admin timezone
create_user_timezone(
    user_id=ADMIN_TELEGRAM_ID,
    user_timedelta=ADMIN_TIMEZONE,
)

amdin_timezone = get_user_timezone(ADMIN_TELEGRAM_ID)
admin_server_timedelta = amdin_timezone.user_server_timedelta

task_to_schedule = [
    # [task, regular_flg, argument, execute_time]
    [
        'send_message',
        True,
        'Полночь. Никакой больше работы!!! 🌙🌌',
        datetime.strptime(
            '00:00',
            REGULAR_TASK_TIME_FORMAT
        ) + admin_server_timedelta,
    ],
    [
        'send_message',
        True,
        'Good morning, World! 😎',
        datetime.strptime(
            '08:59',
            REGULAR_TASK_TIME_FORMAT
        ) + admin_server_timedelta,
    ],
    [
        'send_message',
        True,
        'Полдень. Praise the SUN! 🔥☀️🌻',
        datetime.strptime(
            '12:00',
            REGULAR_TASK_TIME_FORMAT
        ) + admin_server_timedelta,
    ],
    [
        'send_message',
        True,
        '18:00 Рабочий день окончен. 🌈',
        datetime.strptime(
            '18:00',
            REGULAR_TASK_TIME_FORMAT
        ) + admin_server_timedelta,
    ],
    [
        'send_forecat',
        True,
        DEFAULT_OPENWEATHER_REGION,
        datetime.strptime(
            '00:00',
            REGULAR_TASK_TIME_FORMAT
        ) + admin_server_timedelta,
    ],
    [
        'send_forecat',
        True,
        DEFAULT_OPENWEATHER_REGION,
        datetime.strptime(
            '09:00',
            REGULAR_TASK_TIME_FORMAT
        ) + admin_server_timedelta,
    ],
    [
        'send_forecat',
        True,
        DEFAULT_OPENWEATHER_REGION,
        datetime.strptime(
            '12:00',
            REGULAR_TASK_TIME_FORMAT
        ) + admin_server_timedelta,
    ],
    [
        'send_forecat',
        True,
        DEFAULT_OPENWEATHER_REGION,
        datetime.strptime(
            '18:00',
            REGULAR_TASK_TIME_FORMAT
        ) + admin_server_timedelta,
    ]
]


for task_index in range(len(task_to_schedule)):
    task, regular_flg, argument, execute_time = task_to_schedule[task_index]
    try:
        create_task(
            kwargs={
                'id': task_index + 1,
                'author_id': ADMIN_TELEGRAM_ID,
                'regular_task': regular_flg,
                'execute_dttm': execute_time,
                'function': task,
                'arguments': {
                    'user_id': ADMIN_TELEGRAM_ID,
                    'argument': argument
                }
            }
        )
    except ValueError as user_exists:
        print(user_exists)
    except KeyError as wrong_params:
        print(wrong_params)
