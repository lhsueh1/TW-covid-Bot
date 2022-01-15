#!/usr/bin/python
# -*- coding: utf-8 -*-

from PIL import ImageFont, ImageDraw, Image
import textwrap
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


def pic_new(date=None, today_confirmed=None, today_domestic=None, today_imported=None, today_death=None, text="(・∀・)"):
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
    if text == "(・∀・)":
        text = str(today.additional_text)


    text = textwrap.fill(text, width=40, fix_sentence_endings=True, subsequent_indent=" ")
    # if int(today_domestic) != 0:
    #     text.replace("今", "\n\n今")


    confirmed_length = 2154
    if int(today_confirmed) == 0:
        domestic_length = 0
    else:
        domestic_length = int((int(today_domestic) / int(today_confirmed)) * confirmed_length)

    if domestic_length < 300 and domestic_length != 0:
        domestic_length = 300
    elif domestic_length > 1854:
        domestic_length = 1854
    imported_length = confirmed_length - domestic_length
    print(domestic_length, imported_length)

    # date
    background_w = 400
    background_h = 240
    background = Image.new("RGBA",(background_w,background_h),(0,0,0,0))
    font = ImageFont.truetype("NotoSansTC-Regular.otf", 190)
    date_word = center_text(background, font, date, background_w, background_h)


    background_w = 420
    background_h = 250

    background = Image.new("RGBA",(background_w,background_h),(0,50,0,00))
    today_confirmed_word = center_text(background, font, today_confirmed, background_w, background_h)

    background_D = Image.new("RGBA",(domestic_length,background_h),(0,50,0,00))
    today_domestic_word = center_text(background_D, font, today_domestic, domestic_length, background_h)
    background_I = Image.new("RGBA",(imported_length,background_h),(0,50,0,00))
    today_imported_word = center_text(background_I, font, today_imported, imported_length, background_h)


    background = Image.new("RGBA",(background_w,background_h),(0,50,0,00))
    deaths_word = center_text(background, font, today_death, background_w, background_h)


    background_w = 2900
    background_h = 900
    font = ImageFont.truetype("NotoSansTC-Regular.otf", 70)
    background = Image.new("RGBA",(background_w,background_h),(0,50,0,00))
    text_word = center_text(background, font, text, background_w, background_h)


    original = Image.open("src/blank.png")

    #(252, 235, 164)
    domestic_tag = Image.open("src/domestic_tag.png")
    #(250, 208, 160)
    imported_tag = Image.open("src/imported_tag.png")


    img = ImageDraw.Draw(original)
    img.rounded_rectangle((590, 545, 590+domestic_length, 590+455), fill=(252, 235, 164), radius=40)
    img.rounded_rectangle((590+domestic_length, 545, 590+domestic_length+imported_length, 590+455), fill=(250, 208, 160), radius=40)

    original.paste(domestic_tag, (590, 470), domestic_tag)
    if domestic_length == 0:
        original.paste(imported_tag, (590+domestic_length, 470), imported_tag)
    else:
        original.paste(imported_tag, (590+domestic_length-60, 470), imported_tag)
    

    if(int(today_confirmed) == 0):
        img.rounded_rectangle((590+domestic_length, 545, 590+domestic_length+imported_length, 590+455), fill=(223, 237, 234), radius=40)
        background_I = Image.new("RGBA",(imported_length,250),(0,50,0,00))
        today_imported_word = center_text(background_I, ImageFont.truetype("NotoSansTC-Regular.otf", 190), "ヾ(｡>﹏<｡)ﾉﾞo*。", imported_length, 250)
        #original.paste(word, (590, 660), word)

    original.paste(date_word, (1206, 20), date_word)
    original.paste(today_confirmed_word, (117, 660), today_confirmed_word)
    original.paste(today_domestic_word, (590, 660), today_domestic_word)
    original.paste(today_imported_word, (590+domestic_length, 660), today_imported_word)
    original.paste(text_word, (217, 1269), text_word)
    original.paste(deaths_word, (2797, 660), deaths_word)

    

    

    original.save("src/out.png")


    return date


pic_new("0110", "70", "12", "58", "0", "今日新增本土個案為6例男性、6例女性，年齡介於未滿5歲至60多歲。今日新增境外移入個案為27例男性、31例女性，年齡介於未滿5歲至70多歲，分別自美國(27例)、英國(4例)、印尼、菲律賓及澳大利亞(各3例)、阿拉伯聯合大公國、比利時及加拿大(各2例)、卡達、德國、柬埔寨、泰國、哥斯大黎加、中國、愛爾蘭、越南、西班牙及巴西(各1例)移入，另2例調查中。入境日介於去(2021)年12月9日至今(2022)年1月10日。")
