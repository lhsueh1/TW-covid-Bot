#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import Update, ParseMode
import telegram
import traceback
import html
import json
import requests
import re
import random
import api
import pic
import urllib3
import threading
import pytz
import datetime
import git

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
        bot.message.reply_text("Authority needed.")

def restart_and_upgrade(update, context):
    g = git.cmd.Git()
    # 如果有新的版本就pull，印出訊息，並且restart
    status = g.log('HEAD..origin/main')
    if status != "":
        g.pull()
        text = 'Bot is restarting...\n\nUpdate info:\n'+text_adjustment(status)
        update.message.reply_text(text)
        threading.Thread(target=stop_and_restart).start()
    else:
        update.message.reply_text('Already up to date.')

def stop_and_restart():
    """Gracefully stop the Updater and replace the current process with a new one."""
    updater.stop()
    os.execl(sys.executable, sys.executable, *sys.argv)

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

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    #update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f'An exception was raised while handling an update\n'
        #f'<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}'
        f'<pre>update = {str(update)}'
        '</pre>\n\n'
        f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
        f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
        f'<pre>{html.escape(tb_string)}</pre>'
    )

    if update is None:
        context.bot.sendMessage(chat_id="@E36_bb079f22", text=message, parse_mode=ParseMode.HTML)
    else:
        if update.message.chat.username != None and update.message.chat.username != "E36_bb079f22":
            context.bot.sendMessage(chat_id="@E36_bb079f22", text=message, parse_mode=ParseMode.HTML)
        update.message.reply_text("Error. Contact moderator.錯誤")

def today_info(update, context):
    processingMessage = context.bot.sendMessage(chat_id=update.message.chat.id, text="Processing...", disable_notification=True)

    if len(context.args) != 0:
        get = api.get_taiwan_outbreak_information(*context.args)
    else:
        get = api.get_taiwan_outbreak_information()

    text = get[0]

    if get[1] == 0:
        special = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for i in special:
            text = text.replace(i, "\\" + str(i))

        text = text.replace("統計數字如果有誤，請於群組", "````統計數字如果有誤，請於`[群組](t.me/joinchat/VXSevGfKN560hTWH)`告知，我們會立刻更正，謝謝。`\n```")
        if get[2] is not None:
            text = text.replace("疾管署新聞稿及政府資料開放平臺", f"```[疾管署新聞稿]({get[2]})````及政府資料開放平臺\n`")
        text = "```\n" + text + "\n```"


        update.message.reply_text(text, parse_mode='MarkdownV2', disable_web_page_preview=True)


        userName = update.message.from_user.username
        if update.message.chat.username != "E36_bb079f22":
            context.bot.sendMessage(chat_id="@E36_bb079f22", text=str(update.message.from_user.first_name) + " @" + str(userName) + ": today_info")

    else:
        context.bot.sendMessage(chat_id="@E36_bb079f22", text=str(update) + "\n\n" + text + "\n" + get[1])
        update.message.reply_text(text)

    if processingMessage is not None:
        context.bot.deleteMessage(chat_id=update.message.chat_id, message_id=processingMessage['message_id'])

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
            processingMessage = context.bot.sendMessage(chat_id=str(update.message.chat.id), text="Searching for " + str(country), disable_notification=True)

            get = api.get_epidemic_status_by_country(str(country))
            if get != None:
                update.message.reply_text(get)

                if update.message.chat.username != "E36_bb079f22":
                    context.bot.sendMessage(chat_id="@E36_bb079f22", text=str(update.message.from_user.first_name) + " @" + str(userName) + ": search " + country)

            else:
                update.message.reply_text("Where is "+str(country)+"?")
                if update.message.chat.username != "E36_bb079f22":
                    context.bot.sendMessage(chat_id="@E36_bb079f22", text=str(update.message.from_user.first_name) + " @" + str(userName) + ": BAD search " + country)

            if processingMessage is not None:
                context.bot.deleteMessage(chat_id=update.message.chat_id, message_id=processingMessage['message_id'])
    else:
        context.bot.sendMessage(chat_id=str(update.message.chat.id), text="Give me something to search for!")
        if update.message.chat.username != "E36_bb079f22":
            context.bot.sendMessage(chat_id="@E36_bb079f22", text=str(update.message.from_user.first_name) + " @" + str(userName) + ": empty search")

def image(update, context):

    if len(context.args) == 1:
        if context.args[0] == "-h":

            update.message.reply_text("Usage: `/image [date] [today confirmed] [today domestic] [today imported] [today death] [total confirmed] [total deaths]`", parse_mode='MarkdownV2')
            return

    processingMessage = update.message.reply_text("Processing...", disable_notification=True)
    cap = "pic"
    if len(context.args) != 0:
        if len(context.args) < 7:
            update.message.reply_text("手動輸入格式錯誤\n格式：[日期] [今日確診] [今日本土] [今日境外] [今日死亡] [總確診] [總死亡]\n例如：/image 0101 10 6 4 1 100 15")
            return
        date = context.args[0]
        today_confirmed = context.args[1]
        today_domestic = context.args[2]
        today_imported = context.args[3]
        today_death = context.args[4]
        confirmed = context.args[5]
        deaths = context.args[6]
        pic.pic(date, today_confirmed, today_domestic, today_imported, today_death, confirmed, deaths)
    else:
        the_date = pic.pic()
        if str(datetime.datetime.now().strftime("%m%d")) != the_date:
            cap = "這是 " + the_date + " 的資料，今日尚未更新，或沒新增"


    context.bot.sendPhoto(chat_id=update.message.chat_id, photo=open("out.png", "rb"), caption=cap, timeout=20)

    if processingMessage is not None:
        context.bot.deleteMessage(chat_id=update.message.chat_id, message_id=processingMessage['message_id'])

    print()
    userName = update.message.from_user.username
    if update.message.chat.username != "E36_bb079f22":
        context.bot.sendMessage(chat_id="@E36_bb079f22", text=str(update.message.from_user.first_name) + " @" + str(userName) + " : " + str(update.message.text))

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

def today_info_everyday(context, **chat_ids):

    get = api.get_taiwan_outbreak_information()
    text = get[0]
    if get[1] == 0:
        text = text_adjustment(text)

        text = text.replace("統計數字如果有誤，請於群組", "````統計數字如果有誤，請於`[群組](t.me/joinchat/VXSevGfKN560hTWH)`告知，我們會立刻更正，謝謝。`\n```")
        if get[2] is not None:
            text = text.replace("疾管署新聞稿及政府資料開放平臺", f"```[疾管署新聞稿]({get[2]})````及政府資料開放平臺\n`")
        text = "```\n" + text + "\n```"

        print('chat_ids: ', chat_ids)
        if "chat_ids" in chat_ids:
            for id in chat_ids["chat_ids"]:
                context.bot.sendMessage(chat_id=id, text=text, parse_mode='MarkdownV2', disable_web_page_preview=True)
        else:
            group = "@hfjdkg93yreljkghre34"
            control = "@E36_bb079f22"
            lilia = 1211462447
            oud = 710970043

            chat = group
            context.bot.sendMessage(chat_id=chat, text=text, parse_mode='MarkdownV2', disable_web_page_preview=True)

    else:
        chat = "@WeaRetRYiNgtOMakEaBot"
        context.bot.sendMessage(chat_id=chat, text="everyday fail" + "\n\n" + text + "\n" + get[1])

def image_everyday(context, **chat_ids):
    cap = "pic"

    the_date = pic.pic()
    if str(datetime.datetime.now().strftime("%m%d")) == the_date:
        if "chat_ids" in chat_ids:
            for id in chat_ids["chat_ids"]:
                context.bot.sendPhoto(chat_id=id, photo=open("out.png", "rb"), timeout=20)
        else:
            group = "@hfjdkg93yreljkghre34"
            context.bot.sendPhoto(chat_id=group, photo=open("out.png", "rb"), timeout=20)

    else:
        cap = "這是 " + the_date + " 的資料，今日尚未更新，或沒新增"

        group = "@WeaRetRYiNgtOMakEaBot"

        chat = group
        context.bot.sendPhoto(chat_id=chat, photo=open("out.png", "rb"), caption=cap, timeout=20)

def everyday(update, context):
    userName = update.message.from_user.username
    chat = "@WeaRetRYiNgtOMakEaBot"

    if len(context.args) == 1:
        if str(context.args[0]).lower() in {"-h", "help", "-help", "h"}:
            text = '''
Usage: `/everyday [option] [hour] [minute] [days]`

[option]:
    jobs: List all jobs
    rm: Followed by `[name]` of job to remove
    `[name]`: Add a job with specified name
`[hour]`: From 0 to 23
`[minute]`: From 0 to 59
`[days]`: 0-6 correspond to Monday-Sunday

Examples:
Launch default: `/everyday`
List jobs: `/everyday jobs`
Remove DefaultJob: `/everyday rm DefaultJob`
Specify name: `/everyday MyName`
Specify name and time: `/everyday MyName 10 20`
Specify all: `/everyday MyName 10 20 0 1 2 3 4 7`
'''

            update.message.reply_text(text, parse_mode='MarkdownV2')
            return


    if True: #userName == "alsoDazzling" or userName == "nullExistenceException":

        if len(context.args) == 0:  # defult add

            queue_daily(context, task=today_info_everyday)
            queue_daily(context, task=image_everyday, name="1420_Default_image")

            msg = "Default 1420 everyday added\!"
            context.bot.sendMessage(chat_id=chat, text=msg, parse_mode='MarkdownV2', disable_web_page_preview=True)

        elif context.args[0] == "jobs":  # list jobs
            if len(context.job_queue.jobs()) != 0:
                t = context.job_queue.jobs()
                job_names = [job.name for job in t]

                s = ""
                for i in range(len(context.job_queue.jobs())):
                    s += str(job_names[i])
                    s += " at `"
                    s += str(t[i])[-15:-1]
                    s += "` \n"
                context.bot.sendMessage(chat_id=chat, text=s, parse_mode='MarkdownV2', disable_web_page_preview=True)
            else:
                context.bot.sendMessage(chat_id=chat, text="None jobs", parse_mode='MarkdownV2', disable_web_page_preview=True)

        elif len(context.args) == 2:  # remove
            if context.args[0] == "rm":
                job_for_delete = context.job_queue.get_jobs_by_name(str(context.args[1]))
                if len(job_for_delete) > 0:
                    job_for_delete[0].schedule_removal()

                    msg = "Removed " + str(context.args[1])
                    context.bot.sendMessage(chat_id=chat, text=msg, parse_mode='MarkdownV2', disable_web_page_preview=True)
                else:
                    msg = "Nothing to remove"
                    context.bot.sendMessage(chat_id=chat, text=msg, parse_mode='MarkdownV2', disable_web_page_preview=True)

        elif len(context.args) == 1:  # add with specify name
            name = text_adjustment(str(context.args[0]))
            chat_ids = option_to_chat_id(name)

            queue_daily(context, task=today_info_everyday, name=name, chat_ids=chat_ids)
            queue_daily(context, task=image_everyday, name=name, chat_ids=chat_ids)

            msg = name + " at 1420 everyday added\!"
            context.bot.sendMessage(chat_id=chat, text=msg, parse_mode='MarkdownV2', disable_web_page_preview=True)

        elif len(context.args) == 3:  # add with specify name and time
            name = text_adjustment(str(context.args[0]))
            chat_ids = option_to_chat_id(name)

            hour = int(context.args[1])
            minute = int(context.args[2])
            if (hour > 24) or (minute > 60):
                context.bot.sendMessage(chat_id=chat, text="Got to be kidding me. No.")
                return

            queue_daily(context, hour=hour, minute=minute, name=name, chat_ids=chat_ids)
            queue_daily(context, task=image_everyday, hour=hour, minute=minute, name=name, chat_ids=chat_ids)

            msg = name + " at " + str(hour) + str(minute) + " everyday added\!"
            context.bot.sendMessage(chat_id=chat, text=msg, parse_mode='MarkdownV2', disable_web_page_preview=True)

        elif len(context.args) > 3 and len(context.args) < 11:  # add with specify all
            name = text_adjustment(str(context.args[0]))
            chat_ids = option_to_chat_id(name)
            hour = int(context.args[1])
            minute = int(context.args[2])
            if (hour > 24) or (minute > 60):
                context.bot.sendMessage(chat_id=chat, text="Got to be kidding me. No.")
                return

            day_list = [int(i) for i in context.args[3:] if int(i) < 7 and int(i) >= 0]
            day_list.sort()
            days = tuple(day_list)
            queue_daily(context, hour=hour, minute=minute, days=days, name=name, chat_ids=chat_ids)
            queue_daily(context, task=image_everyday, hour=hour, minute=minute, days=days, name=name, chat_ids=chat_ids)

            msg = name + " at " + str(hour) + str(minute) + " on days " + ','.join(str(d) for d in days) + " added\!"
            context.bot.sendMessage(chat_id=chat, text=msg, parse_mode='MarkdownV2', disable_web_page_preview=True)

        elif len(context.args) >= 11:
            context.bot.sendMessage(chat_id=chat, text="Look at what you're typing. No.")
            return

def queue_daily(context,
                task: callable = today_info_everyday,
                hour: int = 14,
                minute: int = 20,
                days: tuple = range(7),
                name = '1420_Default_today_info',
                chat_ids: list = ['@WeaRetRYiNgtOMakEaBot']):

    if chat_ids is None:
        chat_ids = ['@WeaRetRYiNgtOMakEaBot']

    context.job_queue.run_daily(task,
                                datetime.time(hour=hour,
                                              minute=minute,
                                              tzinfo=pytz.timezone('Asia/Taipei')),
                                days=days,
                                name=text_adjustment(name),
                                job_kwargs={'kwargs': {'chat_ids': tuple(chat_ids)}})

def option_to_chat_id(name: str):
    chat_ids = []

    if "channel" in name:
        chat_ids.append("@Taiwanepidemic")
    if text_adjustment("toi_group") in name:
        chat_ids.append("@WeaRetRYiNgtOMakEaBot")

    if not chat_ids:
        chat_ids = None

    return chat_ids

def text_adjustment(text: str):
    special = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for i in special:
        text = text.replace(i, "\\" + str(i))
    return text


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
    dp.add_handler(CommandHandler('restart_and_upgrade', restart_and_upgrade, filters=Filters.user(username=['@alsoDazzling', '@nullExistenceException'])))
    dp.add_handler(CommandHandler("everyday", everyday, pass_job_queue=True))

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
