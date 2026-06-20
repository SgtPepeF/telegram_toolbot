from telegram_bot.bot import telegtam_bot

from weather.bot_commands import (
    bot_send_forecat,
)


@telegtam_bot.message_handler(commands=['forecast'])
def reply_forecast(message):
    return bot_send_forecat(
        user_id=message.from_user.id
    )


@telegtam_bot.message_handler(content_types=('text',))
def common_reply(message):
    TEXT_REPLY = """Команда не распознана."""
    telegtam_bot.reply_to(message, TEXT_REPLY)


if __name__ == '__main__':
    telegtam_bot.infinity_polling()
