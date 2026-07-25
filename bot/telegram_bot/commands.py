"""File containing bot commands.

Note that EVERY bot command should have only 2 arguments:
    - user_telegtam_id for user to send message to
    - another STRING argument

every function must be registered to be used.
"""

from weather.queries import get_user_location
from weather.actions import forecast

from scheduler.actions import (
    get_server_time,
    get_user_time
)

from .bot import telegtam_bot
from .constants import DATETIME_FORMAT


# Looks unnecessary, but with it can schedule messaging.
def send_message(user_id, argument):
    telegtam_bot.send_message(
        chat_id=user_id,
        text=argument
    )


def send_time(user_id, argument=None):
    server_time = get_server_time()
    user_time = get_user_time(user_id)

    reply_text = f"""
        Время на клиенте {user_time.strftime(DATETIME_FORMAT)}
        Время на сервере {server_time.strftime(DATETIME_FORMAT)}
    """.replace('    ', '')
    send_message(
        user_id,
        reply_text
    )


def send_forecat(user_id, argument=None):
    """Sends a forecast to a chosen user."""

    location = argument or (get_user_location(user_id)).location
    if not location:
        return send_message(
            user_id,
            """Бот не знает Ваш город.

            Воспользуйтесь полным вариантом команды
            /погода [город]
            Или зарегистрируйте свой город по умолчанию командой
            /register city [город]
            """.replace('    ', '')
        )
    forecast_text = forecast(city=location)
    send_message(user_id, forecast_text)


def send_help(user_id, argument=None):
    HELP_ACTIONS = {
        'register', 'зарегистрировать',
        'forecast', 'weather', 'погода',
        'time', 'время',
        'plan', 'запланируй',
        'delete', 'удалить',
        'tasks', 'задачи',
        'work', 'работа',
    }

    need_full_help = not argument or argument not in (HELP_ACTIONS)

    HELP_TEXT = ''

    if need_full_help:
        HELP_TEXT += """
            Я -- бот-планировщик Ваших задач🤖⏱️

            👾 Мои возможности:
            • Отправить прогноз погоды по запросу;
            • Запланировать разовое/регулярное сообщение;
            • Запланировать разовое/регулярное действие из списка доступных действий бота.
            • Запустить трекер рабочего времени (в разработке).


            Доступные команды

            ℹ️ /help [команда]
            Присылает в ответ *это* сообщение.
            ✏️ __Примеры команды__:
             --> /help
             --> /помощь
             --> /help weather
             --> /помощь запланировать
        """

    if need_full_help or argument in {'register', 'зарегистрировать'}:
        HELP_TEXT += """

            🏙 /register city [город]
            Сохраняет город, для которого Вы хотите получать прогноз погоды по умолчанию.
            ✏️ __Примеры команды__:
             --> /register city moscow
             --> /зарегистрировать город Екатеринбург

            🕐 /register time [HH:MM]
            Сохраняет указанный часовой пояс UTC. НЕОБХОДИМО для правильной работы планировщика.
            ✏️ __Примеры команды__:
             --> /register time 03:00  [МСК]
             --> /зарегистрировать время 05:00  [ЕКБ]
        """

    if need_full_help or argument in {'time', 'время'}:
        HELP_TEXT += """

            ⏰ /time
            Присылает текущее время пользователя и сервера.
            ✏️ __Примеры команды__:
             --> /time
             --> /время
            ❗️ ВАЖНО: От совпадения отображаемого времени с вашим локальным временем зависит комфорт пользования ботом.
            Используйте команду "/register time [HH:MM]", чтобы указать ваш часовой пояс.
        """

    if need_full_help or argument in {'weather', 'погода', 'forecast'}:
        HELP_TEXT += """

            ☀️ /weather [город]
            Присылает прогноз погоды в указанном Вами, добавленном командой */register city*.
            ✏️ __Примеры команды__:
             --> /погода Москва
             --> /weather perm
             --> /forecast perm
             --> /погода
        """

    if need_full_help or argument in {'plan', 'запланируй'}:
        HELP_TEXT += """

            ⏳ /plan [regular] [date] [time] [task] [argument]
            Запускает планировщик для указанной задачи.
            ✏️__Примеры команды__:
             --> /запланируй регулярно 12:00 погода Екатеринбург
             --> /запланируй 14.03 15:00 сообщение Записаться в к-р-у-ж-о-к любителей математики🤓
             --> /plan regular 09:00 message Hello World🌏!
            🧙Список доступных к планированию задач [task]:
                - message, сообщение
                - weather, погода
        """

    if need_full_help or argument in {'tasks', 'задачи'}:
        HELP_TEXT += """
            📋 /tasks
            Отправляет список всех активных задач пользователя.
            ✏️__Примеры команды__:
             --> /tasks
             --> /задачи
        """

    if need_full_help or argument in {'delete', 'удалить'}:
        HELP_TEXT += """
            🗑 /delete [id]
            Удаляет запланированное действие по его айди.
            ✏️__Примеры команды__:
             --> /delete 13
             --> /delete 91
        """

    if need_full_help or argument in {'work', 'работа'}:
        HELP_TEXT += """
            🚀 /work
            Инициализирует скрипт трекинга рабочего времени.
            По умолчанию выделяет 50 минут на работу и 10 минут на отдых.
            ✏️__Примеры команды__:
             --> /work
             --> /работа
        """

    send_message(user_id, HELP_TEXT.replace('    ', ''))


REGISTERED_BOT_COMMANDS = {
    send_message.__name__: send_message,
    'message': send_message,
    'сообщение': send_message,
    send_forecat.__name__: send_forecat,
    'forecast': send_forecat,
    'погода': send_forecat,
    'прогноз': send_forecat,
}
