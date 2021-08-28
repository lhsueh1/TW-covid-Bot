#!/usr/bin/python
# -*- coding: utf-8 -*-

from PIL import ImageFont, ImageDraw, Image
import api
import datetime
from web_crawler import TodayConfirmed

def center_text(img, font, text, background_w, background_h, color=(0,0,0)):
    draw = ImageDraw.Draw(img)
    text_width, text_height = draw.textsize(text, font)
    position = ((background_w-text_width)/2,(background_h-text_height)/2)
    draw.text(position, text, color, font=font)
    return img



def pic(date=None, today_confirmed=None, today_domestic=None, today_imported=None, today_death=None, confirmed=None, deaths=None):
    epidemic = api.TaiwanEpidemic()
    cdc_url = api.CDC_NEWS_URL
    today = TodayConfirmed(cdc_url)
    if date == None:
        date = str(today.date.strftime("%m%d"))#str(datetime.datetime.now().strftime("%m")) + str(datetime.datetime.now().strftime("%d"))
    if today_confirmed == None:
        today_confirmed = str(today.today_confirmed)
    if today_domestic == None:
        today_domestic = str(today.today_domestic)
    if today_imported == None:
        today_imported = str(today.today_imported)
    if today_death == None:
        today_death = str(today.today_deaths)
    if confirmed == None:
        confirmed = epidemic.confirmed
    if deaths == None:
        deaths = epidemic.deaths



    background_w = 260
    background_h = 90
    background = Image.new("RGBA",(background_w,background_h),(0,0,0,0))
    font = ImageFont.truetype("DejaVuSans.ttf", 80)
    date_word = center_text(background, font, date, background_w, background_h, (255, 255, 255))

    font = ImageFont.truetype("DejaVuSans.ttf", 60)
    background_w = 240
    background_h = 70

    background = Image.new("RGBA",(background_w,background_h),(0,0,0,0))
    today_confirmed_word = center_text(background, font, today_confirmed, background_w, background_h)

    background_small = Image.new("RGBA",(background_w//2,background_h),(0,0,0,0))
    today_domestic_word = center_text(background_small, font, today_domestic, background_w//2, background_h)
    background_small = Image.new("RGBA",(background_w//2,background_h),(0,0,0,0))
    today_imported_word = center_text(background_small, font, today_imported, background_w//2, background_h)

    background = Image.new("RGBA",(background_w,background_h),(0,0,0,0))
    today_death_word = center_text(background, font, today_death, background_w, background_h)
    background = Image.new("RGBA",(background_w,background_h),(0,0,0,0))
    confirmed_word = center_text(background, font, confirmed, background_w, background_h)
    background = Image.new("RGBA",(background_w,background_h),(0,0,0,0))
    deaths_word = center_text(background, font, deaths, background_w, background_h)

    original = Image.open("post.png")
    img = ImageDraw.Draw(original)
    original.paste(date_word, (100, 25), date_word)
    original.paste(today_confirmed_word, (60, 260), today_confirmed_word)
    original.paste(today_domestic_word, (60, 400), today_domestic_word)
    original.paste(today_imported_word, (180, 400), today_imported_word)
    original.paste(today_death_word, (435, 310), today_death_word)
    original.paste(confirmed_word, (60, 750), confirmed_word)
    original.paste(deaths_word, (435, 750), deaths_word)




    original.save("out.png")

    return date

#pic("10")
