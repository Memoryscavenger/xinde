import random
from time import time, localtime

import requests
from bs4 import BeautifulSoup

import cityinfo
from requests import get, post
from datetime import datetime, date
from zhdate import ZhDate
import sys
import os


def get_color():
    # 获取随机颜色
    get_colors = lambda n: list(map(lambda i: "#" + "%06x" % random.randint(0, 0xFFFFFF), range(n)))
    color_list = get_colors(100)
    return random.choice(color_list)


def get_access_token():
    # appId
    app_id = config["app_id"]
    # appSecret
    app_secret = config["app_secret"]
    post_url = ("https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}"
                .format(app_id, app_secret))
    try:
        access_token = get(post_url).json()['access_token']
    except KeyError:
        print("获取access_token失败，请检查app_id和app_secret是否正确")
        os.system("pause")
        sys.exit(1)
    # print(access_token)
    return access_token


def get_weather(province, city):
    # 城市id
    try:
        city_id = cityinfo.cityInfo[province][city]["AREAID"]
    except KeyError:
        print("推送消息失败，请检查省份或城市是否正确")
        os.system("pause")
        sys.exit(1)
    # city_id = 101280101
    # 毫秒级时间戳
    t = (int(round(time() * 1000)))
    headers = {
        "Referer": "http://www.weather.com.cn/weather1d/{}.shtml".format(city_id),
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    url = "http://d1.weather.com.cn/dingzhi/{}.html?_={}".format(city_id, t)
    response = get(url, headers=headers)
    response.encoding = "utf-8"
    response_data = response.text.split(";")[0].split("=")[-1]
    response_json = eval(response_data)
    print(response_json)
    weatherinfo = response_json["weatherinfo"]
    # 天气
    weather = weatherinfo["weather"]
    # 最高气温
    temp = weatherinfo["temp"]
    # 最低气温
    tempn = weatherinfo["tempn"]

    ##===================================================================================
    headers1 = {
        "Referer": "http://www.weather.com.cn/weather1d/{}.shtml".format(city_id),
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    HTML = "https://tianqi.2345.com/pudong1d/71146.htm"

    response1 = requests.get(HTML, headers=headers1)
    response1.encoding = "utf-8"
    my_soup = BeautifulSoup(response1.text, "html.parser")

    # 获取信息主标签
    main_str = my_soup.find("div", attrs={"class": "real-mess"})

    # 获取今天天气、温度
    # weather_main = main_str.find("div", attrs={"class": "real-today"})
    # split = weather_main.text.split("：")[1]
    # # 今天天气
    # weather = split.split("° ")[1]
    # # 最高气温
    # temp = split.split("° ")[0].split("-")[1] + "°C"
    # # 最低气温
    # tempn = split.split("° ")[0].split("-")[0] + "°C"

    # 现在的天气 多云
    now_weather = main_str.find("em", attrs={"class": "cludy"}).text
    find_all = main_str.findAll("span", attrs={"class": "real-data-mess fl"})
    # 当前风向 东北风3级
    wind_direction = find_all[0].text.replace(' ', '')
    # 当前空气湿度 86%
    air_humidity = find_all[1].text.replace('湿度 ', '')
    # 当前紫外线  很弱
    ultraviolet_rays = find_all[2].text.replace('紫外线 ', '')

    # 空气主要标签
    air_main = my_soup.find("div", attrs={"class": "box-mod-tb"})
    # 空气质量  优-16
    air_quality = air_main.find("em").text + "-" + air_main.find("span").text
    # pm 2.5    10
    pm = air_main.find("div", attrs={"class": "aqi-map-style-tip"}).find("em").text

    hours24_main = my_soup.find("div", attrs={"class": "hours24-data-th-right"})
    # 日出时间  06:01
    sunrise = hours24_main.findAll("span")[0].text.split(" ")[1]
    # 日落时间  19:00
    sunset = hours24_main.findAll("span")[1].text.split(" ")[1]

    str_all = """幸福总是在不经意间降临，你需要静静地以一颗平常心去感受。
    # 每日问候
    literature_all = str_all.split("\n")
    greetings_today = random.choice(literature_all)

    return weather, temp, tempn, now_weather, wind_direction, air_humidity, ultraviolet_rays, air_quality, pm, sunrise, sunset, greetings_today
# 获取accessToken
accessToken = get_access_token()
# 接收的用户
users = config["user"]
# 传入省份和市获取天气信息
province, city = config["province"], config["city"]
weather, max_temperature, min_temperature, now_weather, wind_direction, air_humidity, ultraviolet_rays, air_quality, pm, sunrise, sunset, greetings_today = get_weather(
    province, city)

# 获取词霸每日金句
note_ch, note_en = get_ciba()
# 公众号推送消息
for user in users:
    send_message(user, accessToken, city, weather, max_temperature, min_temperature, note_ch, note_en, now_weather,
                 wind_direction, air_humidity, ultraviolet_rays, air_quality, pm, sunrise, sunset, greetings_today)
os.system("pause")
