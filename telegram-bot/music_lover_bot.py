# TODO: REMOVE SENSITIVE INFO
# TODO: CLEAN CODE
# TODO: IMPROVE FOLDER NAVIGATION
# TODO: REMOVE POLLING
# TODO: EXE RUNNING LOCAL


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

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


# def analyze_message(message):

#     from openai import AzureOpenAI

#     client = AzureOpenAI(
#         api_key=os.environ["AZURE_OPENAI_API_KEY"],
#         api_version="2024-02-15-preview",
#         azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
#     )

#     prompt = f"""
#             You are an assistant bot that based on text, provided by user, is able to identify which year and which kind of document is required by the user

#             Extract from the user question the document type and the year required
#             If you find the Answer it MUST BE in json this format following this pattern:
#             {{
#             "doc_type" : "the doc type identified",
#             "year" : "the year identified"
#             }}

#             These are the document type supported
#             f24 : about the f24 document
#             redditi : about the redditi document
#             730 : about the 730 document

#             User Question
#             {message}


#             Response only if the question is about the document type and the year.
#             If not or if you don't know the answer just return an empty string like this: ""

#             Answer:
#     """

#     response = client.chat.completions.create(
#         model="chat",
#         messages=[
#             {"role": "system", "content": prompt},
#         ],
#     )

#     print(response.choices[0].message.content)
#     return response.choices[0].message.content


# def generate_keyboard_from_folder(folder_path, user_root_path):
#     # Create an empty list to hold rows of buttons
#     keyboard = []
#     current_row = []

#     # List all files and directories in the given folder
#     try:
#         items = os.listdir(folder_path)
#     except FileNotFoundError:
#         return None

#     # Get the parent folder path
#     if folder_path != f"./data/{user_root_path}":
#         parent_path = os.path.dirname(folder_path)
#         go_back_button = InlineKeyboardButton("🔙 Go Back", callback_data=f"navigate:{parent_path}")
#         keyboard.append([go_back_button])  # Add the "Go Back" button in a new row at the top


#     # Create a button for each item
#     for index, item in enumerate(items):
#         item_path = os.path.join(folder_path, item)

#         # Check if it is a folder or a file
#         if os.path.isdir(item_path):
#             # For folders, the callback_data sends a command to navigate into the folder
#             callback_data = f"navigate:{item_path}"
#             button_text = f"📁 {item}"
#         else:
#             # For files, the callback_data is for selecting the file
#             callback_data = f"select:{item_path}"
#             button_text = f"📃 {item}"

#         button = InlineKeyboardButton(button_text, callback_data=callback_data)

#         # Add the button to the current row
#         current_row.append(button)

#         # To organize buttons into rows of 2
#         if len(current_row) == 2:
#             keyboard.append(current_row)
#             current_row = []

#     # If there's an odd number of buttons, add the last row
#     if current_row:
#         keyboard.append(current_row)

#     return InlineKeyboardMarkup(keyboard)


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
    login_url = f"http://localhost:8000/bot-login/login?chat_id={chat_id}"
    message = f"Ciao benvenuto. Per iniziare clicca [qui]({login_url})"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # check if the user is in the list of users
    await update.message.reply_text("Ciao")


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
