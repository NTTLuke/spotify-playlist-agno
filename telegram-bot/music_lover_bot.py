import logging
from telegram import (
    Update,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
import json
from dotenv import load_dotenv
import os
import re

load_dotenv()

from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    InlineQueryHandler,
    CallbackQueryHandler,
)
import aiohttp


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


users = ["nttluke"]


def escape_markdown_v2(text):
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    return re.sub(r"([{}])".format(re.escape(escape_chars)), r"\\\1", text)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.username not in users:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Mi spiace ma non ti ho trovato nei miei utenti. Non posso continuare.",
        )
        return

    chat_id = update.message.chat_id

    # check if the user has stored the access token
    login_url = os.getenv("SPOTIFY_LOGIN_URL").format(
        chat_id=chat_id
    )  # f"http://localhost:8000/bot-login/login?chat_id={chat_id}"
    message = f"Ciao benvenuto. Per iniziare clicca [qui]({login_url})"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Construct the API URL
    api_url = "http://localhost:8000/chat"

    # Define the chat request body
    chat_request_body = {
        # Populate with the necessary data for your chat request
        "message": update.message.text,
        "assistant": "SPOTIFY_PLAYLIST",
    }

    # Define the Spotify refresh token
    spotify_access_token = "BQBrRyqJiCoMPvZQT3KouyeNjxTjHwGkOvNBLAQ7tNg7j-XZ5Zb1fNZ8gPvqj1_buj2rnarDblzKf_AD6pzl7oCi50NacqzuKs0sNdzAgFMcPEzhXUoTyDmoz-6Lbuifi66dHtvYNUyfUsEEqMYTTLs6sYnz4XOBZ-aLBm7vDQtC004HUto9DfmtQJD9tuHGnXADaadopQXcU4TxVaGJCMEBlkuy_hC6-wsxldCKxw8Tae0ilPjWx5qNyEYxGNzwNzZ8xqo"

    await update.message.reply_text("Your request is being processed. Please wait...")

    # Make the asynchronous API call
    async with aiohttp.ClientSession() as session:
        headers = {
            "X-SPOTIFY-ACCESS-TOKEN": spotify_access_token,
            "Content-Type": "application/json",
        }

        async with session.post(
            api_url, json=chat_request_body, headers=headers
        ) as response:
            # Handle the API response
            if response.status == 200:
                api_response = await response.text()
                await update.message.reply_text(f"API Response: {api_response}")
            else:
                await update.message.reply_text(
                    f"Failed to call API: {response.status}"
                )


# async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Parses the CallbackQuery and updates the message text."""
#     query = update.callback_query

#     # CallbackQueries need to be answered, even if no notification to the user is needed
#     # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
#     await query.answer()

#     # send the document to the user via telegram
#     input_string = query.data
#     splitted = input_string.split(":", 1)

#     action = splitted[0]
#     folder_path = splitted[1]

#     # Navigate into the folder
#     if action == "navigate":
#         user = find_user_by_username(update.effective_user.username)
#         folder_name = folder_path.split("\\", 1)
#         if len(folder_name) > 1:
#             folder_name = folder_name[1]
#         else:
#             folder_name = "principale della tua azienda"

#         reply_markup = generate_keyboard_from_folder(
#             folder_path=folder_path, user_root_path=str.lower(user["company"])
#         )
#         if reply_markup is None:
#             await query.edit_message_text(
#                 text="Non ci sono documenti in questa cartella."
#             )
#             return
#         await query.edit_message_text(
#             text=f"Ecco i documenti nella cartella {folder_name}.",
#             reply_markup=reply_markup,
#         )
#         return

#     # Open the selected file and insert a string with the name of the requested document
#     with open(folder_path, "w") as file:
#         file.write("This is the file you requested.")

#     await context.bot.send_document(
#         chat_id=query.message.chat_id,
#         document=open(folder_path, "rb"),
#         caption="Ecco il documento richiesto. Se hai bisogno di altro, chiedi pure.",
#     )


# def main_with_polling():
#     application = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_API_KEY")).build()

#     start_handler = CommandHandler("start", start)
#     application.add_handler(start_handler)

#     echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
#     application.add_handler(echo_handler)

#     application.add_handler(CallbackQueryHandler(button))

#     application.run_polling()


def main_with_webhook():

    application = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)

    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    application.add_handler(echo_handler)

    # application.add_handler(CallbackQueryHandler(button))

    # Start the webhook
    application.run_webhook(
        listen="0.0.0.0",
        port=os.getenv("WH_SERVER_PORT"),
        url_path=os.getenv("TELEGRAM_BOT_TOKEN"),
        webhook_url=os.getenv("WH_SERVER_HOST") + os.getenv("TELEGRAM_BOT_TOKEN"),
    )


if __name__ == "__main__":
    main_with_webhook()
