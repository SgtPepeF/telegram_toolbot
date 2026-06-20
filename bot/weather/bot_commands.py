from .weather import forecast

from telegram_bot.bot import telegtam_bot


def bot_send_forecat(user_id, city='perm'):
    """Sends a forecast to a chosen user."""
    bot_reply_text = forecast(city=city)

    telegtam_bot.send_message(
        chat_id=user_id,
        text=bot_reply_text
    )
