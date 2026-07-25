from copy import copy
from datetime import timedelta

from database.queries import create_user
from scheduler.queries import (
    create_task,
    get_task,
    get_user_tasks,
    delete_task,
    create_user_timezone
)
from scheduler.actions import (
    schedule_task,
    unschedule_task,
    get_user_server_timedelta,
    get_task_text_representation
)
from weather.queries import create_location

from .constants import (
    TIME_REGEXP_FORMATS
)
from .bot import telegtam_bot
from .utils import (
    parse_command,
    check_formatting,
)
from .commands import (
    send_message,
    send_time,
    send_forecat,
    send_help,
)
from .utils import pop_first_word


@telegtam_bot.message_handler(commands=['start', 'старт'])
def start(message):
    user = create_user(
        user_kwargs={
            'user_id': message.from_user.id
        }
    )

    send_message(
        user.user_id,
        f'Приветствую, @{user.username}!'
    )

    return send_help(user.user_id)


@telegtam_bot.message_handler(commands=['help', 'помощь'])
def help(message):
    text_to_parse = copy(message.text)
    _, command_argument = pop_first_word(text_to_parse)
    return send_help(
        message.from_user.id,
        command_argument
    )


@telegtam_bot.message_handler(commands=['time', 'время'])
def send_current_time(message):
    return send_time(message.from_user.id)


@telegtam_bot.message_handler(commands=['weather', 'forecast', 'погода'])
def reply_forecast(message):
    text_to_parse = copy(message.text)
    _, command_argument = pop_first_word(text_to_parse)
    return send_forecat(
        user_id=message.from_user.id,
        argument=command_argument
    )


@telegtam_bot.message_handler(commands=['register', 'зарегистрировать'])
def register(message):
    text_to_parse = copy(message.text)
    _, text_to_parse = pop_first_word(text_to_parse)

    if not text_to_parse:
        return send_message(
            message.from_user.id,
            argument=(
                'Команда пуста.\n'
                'Попробуйте "/help register", если возникают трудности.'
            )
        )

    obj_to_reg, argument = pop_first_word(text_to_parse)

    full_actions_to_register = {
        'city', 'город',
        'time', 'время',
    }

    if obj_to_reg not in full_actions_to_register:
        return send_message(
            message.from_user.id,
            f'Неизвестное действие {obj_to_reg}.'
        )

    if not argument or not argument.strip():
        return send_message(
            message.from_user.id,
            argument=(
                f'Недопустимый аргумент для действия {obj_to_reg}.'
                'Попробуйте "/help register", если возникают трудности.'
            )
        )

    # register city [city]
    if obj_to_reg in {'city', 'город'}:
        new_location = create_location(
            location_kwargs={
                'user_id': message.from_user.id,
                'location': argument.strip().capitalize()
            }
        )  # rewrites old location if exists

        return send_message(
            message.from_user.id,
            argument=(
                f'Новая локация успешно установлена: {new_location.location}.\n'
                'Обратите внимание, что бот не проверяет наличие ошибок в локации.'
                'Если локация написана с ошибкой ресурс Open Weather Map может'
                'вернуть статус 404.'
            )
        )

    # /register time 00:00
    if obj_to_reg in {'time', 'время'}:
        time_string = argument.strip().capitalize()
        if not check_formatting(time_string, TIME_REGEXP_FORMATS):
            return send_message(
                message.from_user.id,
                argument=(
                    'Недопустимый формат времени.\n'
                    'Попробуйте "/help register", если возникают трудности.'
                )
            )
        hours, minutes = [int(time) for time in time_string.split(':')]
        user_timedelta = timedelta(hours=hours, minutes=minutes)
        create_user_timezone(
            user_id=message.from_user.id,
            user_timedelta=user_timedelta
        )
        send_message(
            message.from_user.id,
            '⏰✅ Время пользователя успешно обновлено.'
        )
        send_time(message.from_user.id)
        return send_message(
            message.from_user.id,
            (
                'Проверьте, что время в сообщении выше соответствует вашему.\n'
                'Если нет, воспользуйтесь командой /register time [HH:MM]'
            )
        )
    return send_message(
        message.from_user.id,
        argument=(
            f'Недопустимый аргумент для действия {obj_to_reg}.\n'
            f'Попробуйте "/help register", если возникают трудности.'
        )
    )


@telegtam_bot.message_handler(commands=['plan', 'запланируй'])
def plan_action(message):
    try:
        command_arguments = parse_command(message.text)
    except ValueError as command_error:
        return send_message(
            user_id=message.from_user.id,
            argument=command_error
        )

    regular_task = command_arguments.get('regular_task')
    user_execution_time = command_arguments.get('execute_dttm')
    function_to_execute = command_arguments.get('function')
    function_argument = command_arguments.get('argument')
    execution_arguments = {
        'user_id': message.from_user.id,
        'argument': function_argument,
    }

    user_server_timedelta = get_user_server_timedelta(
        user_id=message.from_user.id
    )
    server_execution_time = user_execution_time - user_server_timedelta

    task = create_task(
        kwargs={
            'author_id': message.from_user.id,
            'regular_task': regular_task,
            'execute_dttm': server_execution_time,
            'function': function_to_execute.__name__,
            'arguments': execution_arguments
        }
    )

    schedule_task(
        task_id=str(task.id),
        function=function_to_execute,
        execute_dttm=server_execution_time,
        arguments=execution_arguments,
        regular_task=regular_task,
    )

    task_text_representation = get_task_text_representation(task)

    success_message = f"""
        ✅Задача успешно создана.
        {task_text_representation}

        Если вы хотите удалить задачу, воспользуйтесь командой
        /delete {task.id}
    """.replace('    ', '')

    send_message(
        message.from_user.id,
        success_message
    )


@telegtam_bot.message_handler(commands=['tasks', 'задачи'])
def list_actions(message):
    tasks = get_user_tasks(message.from_user.id)
    if not tasks:
        return send_message(
            message.from_user.id,
            'У Вас нет запланированных задач.'
        )
    reply_text = f'У Вас {len(tasks)} запланированных задач:'

    for task in tasks:
        task_text_representation = get_task_text_representation(task)
        reply_text += f'\n{task_text_representation}'
    reply_text = reply_text.replace('    ', '')
    return send_message(
        message.from_user.id,
        reply_text
    )


@telegtam_bot.message_handler(commands=['delete', 'удалить'])
def delete_action(message):
    text_to_parse = copy(message.text)
    _, task_id = pop_first_word(text_to_parse)

    if not task_id:
        return send_message(
            message.from_user.id,
            argument=(
                'Команда пуста.\n'
                'Попробуйте "/help delete", если возникают трудности.'
            )
        )
    try:
        task_id = int(task_id)
    except ValueError:
        return send_message(
            message.from_user.id,
            argument=(
                'id должен быть целым числом.\n'
                'Попробуйте "/help delete", если возникают трудности.'
            )
        )

    task = get_task(task_id)
    if not task:
        return send_message(
            message.from_user.id,
            argument=(
                'Задачи с указанным id не существует.'
            )
        )
    if task.author_id != message.from_user.id:
        return send_message(
            message.from_user.id,
            argument=(
                'Это не Ваша задача. Задачу может удалить только её автор.'
            )
        )
    unschedule_task(str(task_id))
    delete_task(task_id)
    return send_message(
        message.from_user.id,
        argument=(
            f'Задача {task_id} успешно удалена🗑.'
        )
    )


@telegtam_bot.message_handler(content_types=['text'])
def common_reply(message):
    TEXT_REPLY = """Команда не распознана."""
    telegtam_bot.reply_to(message, TEXT_REPLY)
