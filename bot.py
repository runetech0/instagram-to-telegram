import conf
from instagram_private_api import Client
from telethon import TelegramClient, errors
from datetime import datetime as dt
import datetime
import time
import pprint
import socks
import os
import requests


# ##############################################< Instagram API setup >##############################################

user_name = conf.INSTA_USERNAME
password = conf.INSTA_PASSWORD

target_username = conf.TARGET_USERNAME

instaClient = Client(user_name, password)

# ##############################################< Telegram Client Setup >##############################################

api_id = conf.API_ID
api_hash = conf.API_HASH


if conf.AUTHENTICATION:
    sockProxy = {
        "proxy_type": socks.SOCKS5,
        "addr": conf.SOCKS5_SERVER,
        "port": conf.SOCKS5_PORT,
        "rdns": True,
        "username": conf.USERNAME,
        "password": conf.PASSWORD
    }


if conf.PROXY:
    if conf.AUTHENTICATION:
        if conf.USERNAME is not None and conf.PASSWORD is not None:
            telegramClient = TelegramClient('anon', api_id, api_hash, proxy=sockProxy)
    elif not conf.AUTHENTICATION:
        print(f'Using proxy server {conf.SOCKS5_SERVER}:{conf.SOCKS5_PORT}')
        telegramClient = TelegramClient('anon', api_id, api_hash, proxy=(
            socks.SOCKS5, conf.SOCKS5_SERVER, conf.SOCKS5_PORT))
else:
    telegramClient = TelegramClient('anon', api_id, api_hash)


# ##############################################< Helper functions >##############################################

def createTimestamp(mins=0, hours=0, days=0):
    now = dt.now() - datetime.timedelta(minutes=mins, hours=hours, days=days)
    ttuple = now.timetuple()
    timestamp = time.mktime(ttuple)
    return int(timestamp)


def downloadImg(url):
    if not os.path.isdir('./tmp'):
        os.mkdir('./tmp')
    r = requests.get(url)
    file = open('./tmp/file.jpg', 'wb')
    file.write(r.content)
    file.close()
    return './tmp/file.jpg'


def sendItem(filePath):
    telegramClient.loop.run_until_complete(telegramClient.send_message('@mzafarm', file=filePath))
    if os.path.exists(filePath):
        os.remove(filePath)

# ##############################################< Instagram API Calls >##############################################


userfeed = instaClient.username_feed(target_username, min_timestamp=createTimestamp(days=100))
listOfItems = userfeed['items']
if listOfItems:
    telegramClient.start()
    for item in listOfItems:
        itemUrl = item['image_versions2']['candidates'][0]['url']
        # Item type will be 1 for image and 2 for video.
        itemType = item['media_type']
        if itemType == 1:
            imgPath = downloadImg(itemUrl)
            sendItem(imgPath)
            continue
        if itemType == 2:
            sendItem(itemUrl)
            continue


# ##############################################< Telegram API calls >##############################################
