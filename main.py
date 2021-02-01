import telebot
import time
from telebot import types
import requests
import datetime
import random
import json

from api_key import API_KEY, TOKEN
from stickers import STICKERS

cities = [
    'Aktobe',
    'Astana',
    'Almaty',
    'Shalkar',
    'Aktau',
    'Atyrau',
    'Shymkent',
    'Taraz',
    'Kyzylorda',
    'Semey',
    'Kostanay',
    'Zhezkazgan',
    'Karagandy'
]

bot = telebot.TeleBot(TOKEN)

def getweatherbyname(name):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={name}&appid={API_KEY}'
    # param = {
    #     'lang': 'ru'
    # }
    r = requests.get(url=url)
    with open('data3.txt', 'w') as outfile:
        json.dump(r.json(), outfile, indent=4, separators=(", ", ": "), sort_keys=True)
    print(r.json())
    return r.json()

def getweatherbyloc(lat, lon):
    url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}'
    r = requests.get(url=url)
    return r.json()

menu = types.ReplyKeyboardMarkup(row_width=1)
btn_countries = types.KeyboardButton('cities')
btn_location = types.KeyboardButton('send location', request_location=True)
menu.add(btn_countries, btn_location)

cities_menu = types.InlineKeyboardMarkup()

for each in cities:
    cities_menu.add(types.InlineKeyboardButton(each, callback_data=each))

@bot.message_handler(commands=['start', 'help'])
def commands(message):
    bot.send_message(message.chat.id,
                     'Hello, please use keyboard (or type the name of city) to choose your location or just send me your location',
                     reply_markup=menu)
    bot.send_message(689642806,
                     'start/help bot from user: ' + '@' + str(
                         message.chat.username))


def getdirection(param):
    deg = int(param)
    if 0 <= deg <= 30 or 330 <= deg <= 360:
        return 'North'
    if 30 < deg < 60:
        return 'North East'
    if 60 <= deg <= 120:
        return 'East'
    if 120 < deg < 150:
        return 'South East'
    if 150 <= deg <= 210:
        return 'South'
    if 210 < deg < 240:
        return 'South West'
    if 240 <= deg <= 300:
        return 'West'
    if 300 < deg < 330:
        return 'North West'
    pass

@bot.message_handler(func=lambda message: True, content_types=['location'])
def answerforloc(message):
    lon = message.location.longitude
    lat = message.location.latitude
    print(lon, ' ', lat)
    data = getweatherbyloc(lat=lat, lon=lon)
    if data['cod'] == 200:
        text = ''
        text += 'City: ' + data['name'] + '\n'
        bot.send_message(message.chat.id, text=text)

        text = 'About weather: ' + data['weather'][0]['main'] + ', ' + data['weather'][0]['description'] + '\n'
        bot.send_message(message.chat.id, text=text)
        st_id = getstidweather(param=data['weather'][0]['id'], temp=int(data['main']['temp']) - 273,
                               icon=data['weather'][0]['icon'])
        bot.send_sticker(message.chat.id, data=st_id)

        hours = data['timezone'] / 3600
        systime = datetime.datetime.fromtimestamp(int(data['dt'])).strftime('%H')

        print(datetime.datetime.fromtimestamp(int(data['dt'])).strftime('%Y-%m-%d %H:%M:%S'))
        # text = 'Time of response: ' + datetime.datetime.fromtimestamp(
        #     int(data['dt'])
        # ).strftime('%Y-%m-%d %H:%M:%S') + '\n'
        text = 'Temperature here: ' + str(int(data['main']['temp']) - 273) + '\n'
        text += 'But feels like: ' + str(int(data['main']['feels_like']) - 273) + '\n'
        bot.send_message(message.chat.id, text=text)
        st_id = getstidtemp(temp=data['main']['feels_like'] - 273,
                            date=str((datetime.datetime.strptime(systime, '%H') + datetime.timedelta(hours=hours)).strftime('%H')))
        bot.send_sticker(message.chat.id, data=st_id)

        try:
            try:
                text = 'Rain volume for last 1 hour (in mm): ' + str(data['rain']['1h']) + '\n'
                bot.send_message(message.chat.id, text=text)
            except:
                print('no 1h rain data')
            try:
                text = 'Rain volume for last 3 hour (in mm): ' + str(data['rain']['3h']) + '\n'
                bot.send_message(message.chat.id, text=text)
            except:
                print('no 3h rain data')

        except:
            print('no rain')
        try:
            try:
                text = 'Snow volume for last 1 hour (in mm): ' + str(data['snow']['1h']) + '\n'
                bot.send_message(message.chat.id, text=text)
            except:
                print('no 1h snow data')
            try:
                text = 'Snow volume for last 3 hour (in mm): ' + str(data['snow']['3h']) + '\n'
                bot.send_message(message.chat.id, text=text)
            except:
                print('no 3h snow data')
        except:
            print('no snow')

        text = 'Humidity: ' + str(data['main']['humidity']) + '%' + '\n'
        bot.send_message(message.chat.id, text=text)

        text = 'Wind speed: ' + str(data['wind']['speed']) + '\n'
        text += 'Wind direction: ' + getdirection(data['wind']['deg']) + '\n'
        bot.send_message(message.chat.id, text=text)
        st_id = getstidwind(speed=data['wind']['speed'])
        bot.send_sticker(message.chat.id, data=st_id)

        text = 'Cloudiness: ' + str(data['clouds']['all']) + '%' + '\n'
        bot.send_message(message.chat.id, text=text)
        st_id = getstidcloud(cl=data['clouds']['all'],
                             date=str((datetime.datetime.strptime(systime, '%H') + datetime.timedelta(hours=hours)).strftime('%H')))
        bot.send_sticker(message.chat.id, data=st_id)


        rt = datetime.datetime.fromtimestamp(
                int(data['sys']['sunrise'])
                ).strftime('%Y-%m-%d %H:%M:%S')

        text = 'Time of sunrise: ' + str(datetime.datetime.strptime(rt, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=hours)) + '\n'
        bot.send_message(message.chat.id, text=text)
        bot.send_sticker(message.chat.id, data=STICKERS['sunrise'])

        st = datetime.datetime.fromtimestamp(
                int(data['sys']['sunset'])
                ).strftime('%Y-%m-%d %H:%M:%S')

        text = 'Time of sunset: ' + str(datetime.datetime.strptime(st, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=hours)) + '\n'
        bot.send_message(message.chat.id, text=text)
        bot.send_sticker(message.chat.id, data=STICKERS['sunset'])
        bot.send_message(689642806,
                         'weather req from user: ' + '@' + str(message.chat.username) + ', ' + 'about city: ' + data[
                             'name'])

    elif data['cod'] == '404' and data['message'] == 'city not found':
        bot.send_message(message.chat.id,
                         'Oops.. I did not found the city you searched. Please, be sure that city you typed exists :)')
        bot.send_message(689642806,
                         'weather req from user: ' + '@' + str(message.chat.username) + ', city not found: ' + message.text)

@bot.message_handler(content_types=['text'])
def answerfortext(message):
    if message.text == 'cities':
        bot.send_message(message.chat.id, 'Choose from list or type yourself', reply_markup=cities_menu)
        bot.send_message(689642806, 'cities req from user: ' + '@' + str(message.chat.username))
    else:
        data = getweatherbyname(message.text)
        # print(data['cod'])
        if data['cod'] == 200:
            text = ''
            text += 'City: ' + data['name'] + '\n'
            bot.send_message(message.chat.id, text=text)
            # print(datetime.datetime.fromtimestamp(int(data['dt'])).strftime('%Y-%m-%d %H:%M:%S'))
            # print(data['timezone'])
            text = 'About weather: ' + data['weather'][0]['main'] + ', ' + data['weather'][0]['description'] + '\n'
            bot.send_message(message.chat.id, text=text)
            st_id = getstidweather(param=data['weather'][0]['id'], temp=int(data['main']['temp']) - 273,
                                   icon=data['weather'][0]['icon'])
            bot.send_sticker(message.chat.id, data=st_id)
            hours = data['timezone'] / 3600
            systime = datetime.datetime.fromtimestamp(int(data['dt'])).strftime('%H')
            # text = 'Time of response: ' + datetime.datetime.fromtimestamp(
            #     int(data['dt'])
            # ).strftime('%Y-%m-%d %H:%M:%S') + '\n'
            text = 'Temperature here: ' + str(int(data['main']['temp']) - 273) + '\n'
            text += 'But feels like: ' + str(int(data['main']['feels_like']) - 273) + '\n'
            bot.send_message(message.chat.id, text=text)
            print(str(datetime.datetime.strptime(systime, '%H')))
            st_id = getstidtemp(temp=data['main']['feels_like']-273,
                                date= str((datetime.datetime.strptime(systime, '%H') + datetime.timedelta(hours=hours)).strftime('%H')))
            bot.send_sticker(message.chat.id, data=st_id)
            try:
                try:
                    text = 'Rain volume for last 1 hour (in mm): ' + str(data['rain']['1h']) + '\n'
                    bot.send_message(message.chat.id, text=text)
                except:
                    print('no 1h rain data')
                try:
                    text = 'Rain volume for last 3 hour (in mm): ' + str(data['rain']['3h']) + '\n'
                    bot.send_message(message.chat.id, text=text)
                except:
                    print('no 3h rain data')

            except:
                print('no rain')
            try:
                try:
                    text = 'Snow volume for last 1 hour (in mm): ' + str(data['snow']['1h']) + '\n'
                    bot.send_message(message.chat.id, text=text)
                except:
                    print('no 1h snow data')
                try:
                    text = 'Snow volume for last 3 hour (in mm): ' + str(data['snow']['3h']) + '\n'
                    bot.send_message(message.chat.id, text=text)
                except:
                    print('no 3h snow data')
            except:
                print('no snow')
            text = 'Humidity: ' + str(data['main']['humidity']) + '%' + '\n'
            bot.send_message(message.chat.id, text=text)

            text = 'Wind speed: ' + str(data['wind']['speed']) + '\n'
            text += 'Wind direction: ' + getdirection(data['wind']['deg']) + '\n'
            bot.send_message(message.chat.id, text=text)
            st_id = getstidwind(speed=data['wind']['speed'])
            bot.send_sticker(message.chat.id, data=st_id)

            text = 'Cloudiness: ' + str(data['clouds']['all']) + '%' + '\n'
            bot.send_message(message.chat.id, text=text)
            st_id = getstidcloud(cl=data['clouds']['all'],
                                 date= str((datetime.datetime.strptime(systime, '%H') + datetime.timedelta(hours=hours)).strftime('%H')))
            bot.send_sticker(message.chat.id, data=st_id)

            # text = 'Time of sunrise: ' + datetime.datetime.fromtimestamp(
            #     int(data['sys']['sunrise'])
            # ).strftime('%Y-%m-%d %H:%M:%S') + '\n'
            # bot.send_message(message.chat.id, text=text)
            # bot.send_sticker(message.chat.id, data=STICKERS['sunrise'])
            #
            # text = 'Time of sunset: ' + datetime.datetime.fromtimestamp(
            #     int(data['sys']['sunset'])
            # ).strftime('%Y-%m-%d %H:%M:%S') + '\n'
            # bot.send_message(message.chat.id, text=text)
            # bot.send_sticker(message.chat.id, data=STICKERS['sunset'])

            rt = datetime.datetime.fromtimestamp(
                int(data['sys']['sunrise'])
            ).strftime('%Y-%m-%d %H:%M:%S')
            print(rt)
            text = 'Time of sunrise: ' + str(
                datetime.datetime.strptime(rt, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=hours)) + '\n'
            print(text)
            bot.send_message(message.chat.id, text=text)
            bot.send_sticker(message.chat.id, data=STICKERS['sunrise'])

            st = datetime.datetime.fromtimestamp(
                int(data['sys']['sunset'])
            ).strftime('%Y-%m-%d %H:%M:%S')

            text = 'Time of sunset: ' + str(
                datetime.datetime.strptime(st, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=hours)) + '\n'
            bot.send_message(message.chat.id, text=text)
            bot.send_sticker(message.chat.id, data=STICKERS['sunset'])
            bot.send_message(689642806, 'weather req from user: ' + '@' + str(message.chat.username) + ', ' + 'about city: ' + data['name'])
        elif data['cod'] == '404' and data['message'] == 'city not found':
                bot.send_message(message.chat.id,
                             'Oops.. I did not found the city you searched. Please, be sure that city you typed exists :)')
                bot.send_message(689642806,
                                 'weather req from user: ' + '@' + str(
                                     message.chat.username) + ', city not found: ' + message.text)
        # else:
        #     text = 'Smthg went wrong :( ' + '\n' + data['message']
        #     bot.send_message(call.message.chat.id, text=text)


def getstidweather(param, temp=0, icon=''):
    if 200 <= param <= 232:
        return STICKERS['st200']
    elif 300 <= param <= 321:
        return STICKERS['st300'][random.randint(0,1)]
    elif 500 <= param <= 531:
        return STICKERS['st500'][random.randint(0, 1)]
    elif 600 <= param <= 622:
        if temp < -15:
            return STICKERS['st600'][0]
        else:
            return STICKERS['st600'][1]
    elif 700 <= param <= 741:
        return STICKERS['st700']
    elif 751 <= param <= 761:
        return STICKERS['st751']
    elif 762 <= param <= 781:
        return STICKERS['st762']
    elif param == 800:
        if icon == '01d':
            return STICKERS['80001d']
        elif icon == '01n':
            return STICKERS['80001n']
    elif 801 <= param <= 804:
        if icon == '02d':
            return STICKERS['02d']
        elif icon == '02n':
            return STICKERS['02n']
        elif icon == '03d':
            return STICKERS['03d']
        elif icon == '03n':
            return STICKERS['03n']
        elif icon == '04d' or icon == '04n':
            return STICKERS['04']
    pass


def getstidtemp(temp, date):
    t = int(date)
    if 6 <= t <= 18:
        if temp >= 30:
            return STICKERS['very_hot'][1]
        elif 20 <= temp < 30:
            return STICKERS['normalday']
        elif 5 < temp < 20:
            return STICKERS['notsoday']
        elif temp <= 5:
            return STICKERS['cold']
    else:
        if temp >= 30:
            return STICKERS['very_hot'][0]
        elif 20 <= temp < 30:
            return STICKERS['normalnight']
        elif 5 < temp < 20:
            return STICKERS['notsonight']
        elif temp <= 5:
            return STICKERS['cold']
    pass


def getstidwind(speed):
    if speed >= 5:
        return STICKERS['wind5']
    else:
        return STICKERS['wind4']
    pass


def getstidcloud(cl, date):
    t = int(date)
    if 6 <= t <= 18:
        if cl < 30:
            return STICKERS['80001d']
        elif 30 <= cl < 60:
            return STICKERS['02d']
        else:
            return STICKERS['03d']
    else:
        if cl < 30:
            return STICKERS['80001n']
        elif 30 <= cl < 60:
            return STICKERS['02n']
        else:
            return STICKERS['03n']
    pass


@bot.callback_query_handler(func=lambda call:True)
def callback(call):
    data = getweatherbyname(call.data)
    # print(call.data)
    if data['cod'] == 200:

        ###########################################################
        text = ''
        text += 'City: ' + data['name'] + '\n'
        bot.send_message(call.message.chat.id, text=text)

        text = 'About weather: ' + data['weather'][0]['main'] + ', ' + data['weather'][0]['description'] + '\n'
        bot.send_message(call.message.chat.id, text=text)
        st_id = getstidweather(param=data['weather'][0]['id'], temp=int(data['main']['temp']) - 273, icon=data['weather'][0]['icon'])
        bot.send_sticker(call.message.chat.id, data=st_id)

        hours = data['timezone'] / 3600
        systime = datetime.datetime.fromtimestamp(int(data['dt'])).strftime('%H')

        # text = 'Time of response: ' + datetime.datetime.fromtimestamp(
        #     int(data['dt'])
        # ).strftime('%Y-%m-%d %H:%M:%S') + '\n'
        text = 'Temperature here: ' + str(int(data['main']['temp']) - 273) + '\n'
        text += 'But feels like: ' + str(int(data['main']['feels_like']) - 273) + '\n'
        bot.send_message(call.message.chat.id, text=text)
        st_id = getstidtemp(temp=data['main']['feels_like']-273,
                            date=str((datetime.datetime.strptime(systime, '%H') + datetime.timedelta(hours=hours)).strftime('%H')))
        bot.send_sticker(call.message.chat.id, data=st_id)

        try:
            try:
                text = 'Rain volume for last 1 hour (in mm): ' + str(data['rain']['1h']) + '\n'
                bot.send_message(call.message.chat.id, text=text)
            except:
                print('no 1h rain data')
            try:
                text = 'Rain volume for last 3 hour (in mm): ' + str(data['rain']['3h']) + '\n'
                bot.send_message(call.message.chat.id, text=text)
            except:
                print('no 3h rain data')

        except:
            print('no rain')
        try:
            try:
                text = 'Snow volume for last 1 hour (in mm): ' + str(data['snow']['1h']) + '\n'
                bot.send_message(call.message.chat.id, text=text)
            except:
                print('no 1h snow data')
            try:
                text = 'Snow volume for last 3 hour (in mm): ' + str(data['snow']['3h']) + '\n'
                bot.send_message(call.message.chat.id, text=text)
            except:
                print('no 3h snow data')
        except:
            print('no snow')

        text = 'Humidity: ' + str(data['main']['humidity']) + '%' + '\n'
        bot.send_message(call.message.chat.id, text=text)

        text = 'Wind speed: ' + str(data['wind']['speed']) + '\n'
        text += 'Wind direction: ' + getdirection(data['wind']['deg']) + '\n'
        bot.send_message(call.message.chat.id, text=text)
        st_id = getstidwind(speed = data['wind']['speed'])
        bot.send_sticker(call.message.chat.id, data=st_id)

        text = 'Cloudiness: ' + str(data['clouds']['all']) + '%' + '\n'
        bot.send_message(call.message.chat.id, text=text)
        st_id = getstidcloud(cl = data['clouds']['all'],
                             date=str((datetime.datetime.strptime(systime, '%H') + datetime.timedelta(hours=hours)).strftime('%H')))
        bot.send_sticker(call.message.chat.id, data=st_id)

        # text = 'Time of sunrise: ' + datetime.datetime.fromtimestamp(
        #     int(data['sys']['sunrise'])
        # ).strftime('%Y-%m-%d %H:%M:%S') + '\n'
        # bot.send_message(call.message.chat.id, text=text)
        # bot.send_sticker(call.message.chat.id, data=STICKERS['sunrise'])
        #
        # text = 'Time of sunset: ' + datetime.datetime.fromtimestamp(
        #     int(data['sys']['sunset'])
        # ).strftime('%Y-%m-%d %H:%M:%S') + '\n'
        # bot.send_message(call.message.chat.id, text=text)
        # bot.send_sticker(call.message.chat.id, data=STICKERS['sunset'])


        rt = datetime.datetime.fromtimestamp(
            int(data['sys']['sunrise'])
        ).strftime('%Y-%m-%d %H:%M:%S')

        text = 'Time of sunrise: ' + str(
            datetime.datetime.strptime(rt, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=hours)) + '\n'
        bot.send_message(call.message.chat.id, text=text)
        bot.send_sticker(call.message.chat.id, data=STICKERS['sunset'])

        st = datetime.datetime.fromtimestamp(
            int(data['sys']['sunset'])
        ).strftime('%Y-%m-%d %H:%M:%S')

        text = 'Time of sunset: ' + str(
            datetime.datetime.strptime(st, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=hours)) + '\n'
        bot.send_message(call.message.chat.id, text=text)
        bot.send_sticker(call.message.chat.id, data=STICKERS['sunset'])
        bot.send_message(689642806,
                         'weather req from user: ' + '@' + str(call.message.chat.username) + ', ' + 'about city: ' + data[
                             'name'])

        ##########################################################
    elif data['cod'] == '404' and data['message'] == 'city not found':
        bot.send_message(call.message.chat.id,
                         'Oops.. I did not found the city you searched. Please, be sure that city you typed exists :)')
        bot.send_message(689642806,
                         'weather req from user: ' + '@' + str(call.message.chat.username) + ', city not found: ' + call.data)
    # else:
    #     text = 'Smthg went wrong :( ' + '\n' + data['message']
    #     bot.send_message(call.message.chat.id, text=text)

# @bot.message_handler(content_types=['sticker'])
# def getid(m):
#     print(m.sticker.file_id)

while True:
    try:
        bot.polling()
    except:
        time.sleep(10)
