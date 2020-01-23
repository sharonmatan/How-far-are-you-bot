import json
import logging
import typing
from cmath import sin, cos, sqrt, asin
from math import radians
from typing import Union
import requests
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
import bot_settings1

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

LOCATION, GET_LOCATION = range(2)

distance = {}
params = {
    'q': "",
    'format': 'json',
    'limit': 1,
}


def start(update, context):
    update.message.reply_text(
        'Hi! where do you want to go?')
    return GET_LOCATION


def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371
    return c * r


def get_location(update, context):
    global distance
    user_text = update.message.text
    params['q'] = user_text
    r = requests.get("https://nominatim.openstreetmap.org/search", params)
    r.raise_for_status()  # will raise an exception for HTTp status code != 200
    data = r.json()
    distance["destination"] = float(data[0]['lon']), float(data[0]['lat'])
    print(distance)
    update.message.reply_text(f"Great!!! \n let's check how far it is... \n please send your location")
    return LOCATION


def location(update, context):
    global distance
    user = update.message.from_user
    user_location = update.message.location
    logger.info("Location of %s: %f / %f", user.first_name, user_location.latitude,
                user_location.longitude)
    distance["my_location"] = user_location.longitude, user_location.latitude
    final_distance = str(haversine(*distance["my_location"], *distance["destination"]))
    update.message.reply_text(f'You are {final_distance[1:7]} km away from {params["q"]}')
    return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(token=bot_settings1.BOT_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            LOCATION: [MessageHandler(Filters.location, location)],
            GET_LOCATION: [MessageHandler(Filters.text, get_location)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
