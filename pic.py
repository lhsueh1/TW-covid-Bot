#!/usr/bin/python
# -*- coding: utf-8 -*-

from PIL import ImageFont, ImageDraw, Image
import matplotlib.pyplot as plt 
import numpy as np
import textwrap
import json
import statistics

import api
import datetime
from TodayInfo import TodayConfirmed


def center_text(img, font, text, background_w, background_h, color=(0,0,0)):
    draw = ImageDraw.Draw(img)
    text_width, text_height = draw.textsize(text, font)
    position = ((background_w-text_width)/2,(background_h-text_height)/2)
    draw.text(position, text, color, font=font)
    return img

def plot_stats():
    xpoints = np.array(list(range(14)))

    with open(r"history_data.json", "r") as jsonFile1:
        history = json.load(jsonFile1)


    weeks_data = history["confirmed"]
    avg_list = history["average"]

    jsonFile1.close()
    
    weeks_data.reverse()
    ypoints = np.array(weeks_data)

    
    avg_list.reverse()
    yavg = np.array(avg_list)

    # ypoints = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    # yavg = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])


    plt.figure(frameon=False).set_figheight(1)
    plt.axis('off')
    
    
    plt.bar(xpoints, ypoints, color = '#cdf3f6', width = 0.9)
    for i in range(len(weeks_data)):
        plt.text(i, ypoints[i], ypoints[i], ha = 'center', fontsize=5)

    plt.plot(yavg, marker = 'o', ms = 2, color = '#47BAED', linewidth = '1')

    plt.savefig('plot.png', dpi=500)

    return avg_list[-1], sum(weeks_data[7:])

def add_to_json_queue(date="1313", today_confirmed=0):
    with open(r"history_data.json", "r") as jsonFile1:
        history = json.load(jsonFile1)

    confirmed_history_list = history["confirmed"]
    average_history_list = history["average"]
    dates_history_list = history["dates"]

    if(dates_history_list[0] == date):
        return

    confirmed_history_list.pop()
    average_history_list.pop()
    dates_history_list.pop()

    confirmed_history_list.insert(0, today_confirmed)

    today_average = int(statistics.mean(confirmed_history_list[:7]))
    average_history_list.insert(0, today_average)

    dates_history_list.insert(0, date)

    history["confirmed"] = confirmed_history_list
    history["average"] = average_history_list

    with open("history_data.json", "w", encoding='utf-8') as jsonFile2:
        json.dump(history, jsonFile2, indent=4)

    jsonFile1.close()
    jsonFile2.close()


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



def pic_stat(date=None, today_confirmed=None, today_domestic=None, today_imported=None, today_death=None, text="(・∀・)"):
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

    add_to_json_queue(date, int(today_domestic))


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
    background_h = 220
    background = Image.new("RGBA",(background_w,background_h),(0,50,0,00))
    font = ImageFont.truetype("DejaVuSans.ttf", 160)
    date_word = center_text(background, font, date, background_w, background_h)

    background_w = 420
    background_h = 250
    font = ImageFont.truetype("NotoSansTC-Regular.otf", 190)
    # today_confirmed
    background = Image.new("RGBA",(background_w,background_h),(0,50,0,00))
    today_confirmed_word = center_text(background, font, today_confirmed, background_w, background_h)

    background_D = Image.new("RGBA",(domestic_length,background_h),(0,50,0,00))
    today_domestic_word = center_text(background_D, font, today_domestic, domestic_length, background_h)
    background_I = Image.new("RGBA",(imported_length,background_h),(0,50,0,00))
    today_imported_word = center_text(background_I, font, today_imported, imported_length, background_h)
    # death
    background = Image.new("RGBA",(background_w,background_h),(0,50,0,00))
    deaths_word = center_text(background, font, today_death, background_w, background_h)

    # text
    background_w = 2900
    background_h = 700
    font = ImageFont.truetype("NotoSansTC-Regular.otf", 70)
    background = Image.new("RGBA",(background_w,background_h),(0,50,0,00))
    text_word = center_text(background, font, text, background_w, background_h)


    original = Image.open("src/blank.png")

    #(205, 243, 246)
    domestic_tag = Image.open("src/domestic_tag.png")
    #(250, 208, 160)
    imported_tag = Image.open("src/imported_tag.png")


    img = ImageDraw.Draw(original)
    img.rounded_rectangle((590, 545, 590+domestic_length, 590+455), fill=(205, 243, 246), radius=40)
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

    original.paste(date_word, (170, 27), date_word)
    original.paste(today_confirmed_word, (117, 660), today_confirmed_word)
    original.paste(today_domestic_word, (590, 660), today_domestic_word)
    original.paste(today_imported_word, (570+domestic_length, 660), today_imported_word)
    original.paste(text_word, (217, 1240), text_word)
    original.paste(deaths_word, (2797, 660), deaths_word)

    
    # plot
    avg, total = plot_stats()
    plot = Image.open("plot.png")
    original.paste(plot, (-513, 2055), plot)

    color = (247, 160, 175)
    if avg > int(today_domestic):
        color = (218, 247, 160)
    img.rounded_rectangle((2300, 2155, 3217, 2155+180), fill=(250,250,250), radius=40)

    img.rounded_rectangle((3217-250, 2155, 3217, 2155+180), fill=color, radius=40)
    # img.ellipse((3217-200-10, 2155+10, 3217-10, 2155+200+10), fill=color)

    background_w = 600
    background_h = 180
    font = ImageFont.truetype("NotoSansTC-Regular.otf", 50)
    background = Image.new("RGBA",(background_w,background_h),(0,50,0,00))
    stats_text = "7-day average: " + str(avg) + "\n7-day sum: " + str(total)
    avg_word = center_text(background, font, stats_text, background_w, background_h, (71, 186, 237))
    original.paste(avg_word, (2300, 2155), avg_word)


    original.save("src/out.png")


    
    return date


# pic_stat("0204", "71", "25", "46", "0", "Regarding the domestic cases, they are 14 men and 11 women, aged between under five and 79 years.Regarding the 46 new imported cases, they are 26 men and 20 women, aged between under ten and 79. 29 of them arrived in Taiwan from the US (seven cases), the Philippines (three cases), Australia (three cases), the Netherlands (two cases), India (two cases), Peru (two cases), Vietnam (two cases), Thailand (two cases), Japan, Nigeria, Canada, Israel, Hong Kong, and China; the areas where the remaining 17 cases arrived are being investigated. They arrived between January 15 and February 4, 2022.")
# pic_stat()
