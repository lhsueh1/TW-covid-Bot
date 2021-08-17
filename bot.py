#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Update
import telegram
import requests
import re
import random
import api
import pic
import urllib3
import threading

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

logger = logging.getLogger(__name__)

'''
    {'update_id': 861268396,
    'message':
        {'message_id': 193, 'date': 1623382445,
        'chat':
             {'id': -1001444774051,
            'type': 'supergroup',
            'title': 'Bot data',
            'username': 'E36_bb079f22'},
        'text': '/start@EpaperTest1_bot',
        'entities': [{'type': 'bot_command', 'offset': 0, 'length': 22}],
        'caption_entities': [],
        'photo': [],
        'new_chat_members': [],
        'new_chat_photo': [],
        'delete_chat_photo': False,
        'group_chat_created': False,
        'supergroup_chat_created': False,
        'channel_chat_created': False,
        'from':
            {'id': 1211462447,
            'first_name': 'Lilia',
            'is_bot': False,
            'username': 'alsoDazzling',
            'language_code': 'en'}
        }
    }

    {'update_id': 192957417,
    'message':
        {'message_id': 182, 'date': 1628439002,
        'chat':
            {'id': 1211462447,
            'type': 'private',
            'username': 'alsoDazzling',
            'first_name': 'Lilia'},
        'text': '/start',
        'entities': [{'type': 'bot_command', 'offset': 0, 'length': 6}],
        'caption_entities': [],
        'photo': [],
        'new_chat_members': [],
        'new_chat_photo': [],
        'delete_chat_photo': False,
        'group_chat_created': False,
        'supergroup_chat_created': False,
        'channel_chat_created': False,
        'from':
            {'id': 1211462447,
            'first_name': 'Lilia',
            'is_bot': False,
            'username': 'alsoDazzling',
            'language_code': 'en'}
        }
    }
'''


def shutdown():
    global updater
    updater.stop()
    updater.is_idle = False

def stop(bot, update):
    '''
    DO NOT TOUCH
    '''
    userName = bot.message.from_user.username
    if userName == "alsoDazzling" or userName == "nullExistenceException":
        bot.message.reply_text("Bye")
        if bot.message.chat.username != "E36_bb079f22":
            update.bot.sendMessage(chat_id="@E36_bb079f22", text="closed")
        threading.Thread(target=shutdown).start()

    else:
        update.message.reply_text("Authority needed")

def start(update, context):
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_text("Start.開始")

    userName = update.message.from_user.username
    if update.message.chat.username != "E36_bb079f22":
        context.bot.sendMessage(chat_id="@E36_bb079f22", text="@" + str(userName) + " " + str(update.message.from_user.first_name) + " : start")

def help(update, context):
    """Send a message when the command /help is issued."""
    userName = update.message.from_user.username
    ID = update.message.chat.id
    if len(context.args) == 0:
        update.message.reply_text("Type in question for more help.\n請輸入遇到的問題")
        if update.message.chat.username != "E36_bb079f22":
            context.bot.sendMessage(chat_id="@E36_bb079f22", text=str(update.message.from_user.first_name) + " @" + str(userName) + "\t" + str(ID) + ": help")
    else:
        if update.message.chat.username != "E36_bb079f22":
            context.bot.sendMessage(chat_id="@E36_bb079f22", text=str(update.message.from_user.first_name) + " @" + str(userName) + "\t" + str(ID) + "\n" + str(update.message.text))

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning("Update '%s' caused error '%s'", update, context.error)
    if update.message.chat.username != None and update.message.chat.username != "E36_bb079f22":
        context.bot.sendMessage(chat_id="@E36_bb079f22", text=str(update) + "\n\n" + str(context.error))
    update.message.reply_text("Error. Contact moderator.錯誤")

def today_info(update, context):
    context.bot.sendMessage(chat_id=update.message.chat.id, text="Processing...")
    get = api.get_taiwan_outbreak_information()
    
    text = get[0]

    if get[1] == 0:
        re = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for i in re:
            text = text.replace(i, "\\" + str(i))

        text = text.replace("統計數字如果有誤，請於群組", "````統計數字如果有誤，請於`[群組](t.me/joinchat/VXSevGfKN560hTWH)`告知，我們會立刻更正，謝謝。`\n```")
        text = text.replace("疾管署新聞稿及政府資料開放平臺", f"```[疾管署新聞稿]({get[2]})````及政府資料開放平臺\n`")
        text = "```\n" + text + "\n```"


        update.message.reply_text(text, parse_mode='MarkdownV2', disable_web_page_preview=True)


        userName = update.message.from_user.username
        if update.message.chat.username != "E36_bb079f22":
            context.bot.sendMessage(chat_id="@E36_bb079f22", text=str(update.message.from_user.first_name) + " @" + str(userName) + ": today_info")

        context.bot.deleteMessage(chat_id=update.message.chat_id, message_id=update.message.message_id+1)
    else:
        context.bot.sendMessage(chat_id="@E36_bb079f22", text=str(update) + "\n\n" + text + "\n" + get[1])
        update.message.reply_text(text)

def search(update, context):
    userName = update.message.from_user.username
    if len(context.args) != 0:
        if context.args[0] == "hi":
            context.bot.sendMessage(chat_id=str(update.message.chat.id), text="Hi there")
            if update.message.chat.username != "E36_bb079f22":
                context.bot.sendMessage(chat_id="@E36_bb079f22", text=str(update.message.from_user.first_name) + " @" + str(userName) + ": search hi")
        elif context.args[0] == "歐東":
            update.message.reply_text("@nullExistenceException 出來打架")
        else:
            country = update.message.text[len(update.message.text.split()[0])+1:]
            context.bot.sendMessage(chat_id=str(update.message.chat.id), text="Searching for " + str(country))

            get = api.get_epidemic_status_by_country(str(country))
            if get != None:
                update.message.reply_text(get)

                if update.message.chat.username != "E36_bb079f22":
                    context.bot.sendMessage(chat_id="@E36_bb079f22", text=str(update.message.from_user.first_name) + " @" + str(userName) + ": search " + country)

            else:
                update.message.reply_text("Where is "+str(country)+"?")
                if update.message.chat.username != "E36_bb079f22":
                    context.bot.sendMessage(chat_id="@E36_bb079f22", text=str(update.message.from_user.first_name) + " @" + str(userName) + ": BAD search " + country)
    else:
        context.bot.sendMessage(chat_id=str(update.message.chat.id), text="Give me something to search for!")
        if update.message.chat.username != "E36_bb079f22":
            context.bot.sendMessage(chat_id="@E36_bb079f22", text=str(update.message.from_user.first_name) + " @" + str(userName) + ": empty search")

def image(update, context):
    update.message.reply_text("Processing...")
    if len(context.args) != 0:
        date = context.args[0]
        today_confirmed = context.args[1]
        today_domestic = context.args[2]
        today_imported = context.args[3]
        today_death = context.args[4]
        confirmed = context.args[5]
        deaths = context.args[6]
        pic.pic(date, today_confirmed, today_domestic, today_imported, today_death, confirmed, deaths)
    else:
        pic.pic()

    context.bot.sendPhoto(chat_id=update.message.chat_id, photo=open("out.png", "rb"), caption="pic", timeout=20)
    context.bot.deleteMessage(chat_id=update.message.chat_id, message_id=update.message.message_id+1)

    print()
    userName = update.message.from_user.username
    if update.message.chat.username != "E36_bb079f22":
        context.bot.sendMessage(chat_id="@E36_bb079f22", text=str(update.message.from_user.first_name) + " @" + str(userName) + " : " + str(update.message.text))

def test(update, context):
    update.message.reply_text("test")

    userName = update.message.from_user.username
    if update.message.chat.username != "E36_bb079f22":
        context.bot.sendMessage(chat_id="@E36_bb079f22", text="@" + str(userName) + " " + str(update.message.from_user.first_name) + " : test")

def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)

COUNT = 0
def chat(update, context):
    userName = update.message.from_user.username
    ID = update.message.chat.id
    global COUNT
    #record user
    if (update.message.chat.username != "E36_bb079f22") and (update.message.chat.type == "private"):
        context.bot.sendMessage(chat_id="@E36_bb079f22", text="@" + str(userName) + "\t" + str(ID) + "\n" + str(update.message.text))
        #context.bot.sendMessage(chat_id="@E36_bb079f22", text=str(update))


        if COUNT < 2:
            update.message.reply_text("I'm not a chat bot.")
            COUNT += 1
    #talk to user
    else:
        message = str(update.message.text)
        try:
            recipient  = int(message.split()[0])

            text = message[len(message.split()[0]):]
            context.bot.sendMessage(chat_id=recipient, text=text)
            COUNT = 0
        except:
            pass

def sticker(update, context):
    #reply sticker to user
    if update.message.chat.username == "nullExistenceException" and (update.message.chat.type == "private"):
        stickerCute = random.choice(["src/cute.tgs", "src/cute2.tgs", "src/cute3.tgs", "src/cute4.webp", "src/cute5.webp", "src/cute6.tgs", "src/cute7.tgs"])
        context.bot.sendSticker(chat_id=update.message.chat_id, sticker=open(stickerCute, "rb"))

    if update.message.chat.username != "E36_bb079f22" and (update.message.chat.type == "private"):
        if update.message.chat.username != "nullExistenceException":
            stickerUgly = random.choice(["src/sticker.tgs", "src/sticker2.tgs", "src/sticker3.tgs", "src/sticker4.tgs", "src/sticker5.tgs", "src/sticker6.tgs", "src/sticker7.tgs", "src/sticker8.tgs", "src/sticker9.tgs"])
            context.bot.sendSticker(chat_id=update.message.chat_id, sticker=open(stickerUgly, "rb"))

        context.bot.sendMessage(chat_id="@E36_bb079f22", text="@" + str(update.message.from_user.username) + ":")
        context.bot.sendSticker(chat_id="@E36_bb079f22", sticker=update.message.sticker)

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    f = open("api-token", "r")
    token = f.read().strip()
    global updater
    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("today_info", today_info))
    dp.add_handler(CommandHandler("search", search))
    dp.add_handler(CommandHandler("image", image))
    dp.add_handler(CommandHandler("stop", stop))

    dp.add_handler(MessageHandler(Filters.text, chat))
    dp.add_handler(MessageHandler(Filters.sticker, sticker))

    

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
