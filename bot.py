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
target_group = conf.TELEGRAM_GROUP_ID


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
    telegramClient.loop.run_until_complete(telegramClient.send_message(target_group, file=filePath))
    if os.path.exists(filePath):
        os.remove(filePath)

# ##############################################< Main function >##############################################


def main():
    try:

        try:
            print('[+] Starting the telegram client...')
            telegramClient.start()
            print('[+] Telegram client started...')
        except KeyboardInterrupt:
            print('[+] Quiting bot...\n')
            exit()
        except errors.rpcerrorlist.ApiIdInvalidError:
            print('[-] Could not start telegram client...')
            print("[-] Invalid API_ID/API_HASH For Telegram...")
            exit()

        while True:
            print('[+] Getting instagram feeds....')
            userfeed = instaClient.username_feed(target_username, min_timestamp=createTimestamp(days=3))
            listOfItems = userfeed['items']
            if listOfItems:
                print('[+] New Instagram feeds found...\n[+] Sending feeds to telegram group...')
                for item in listOfItems:
                    # Item type will be 1 for image and 2 for video.
                    itemType = item['media_type']
                    if itemType == 1:
                        itemUrl = item['image_versions2']['candidates'][0]['url']
                        imgPath = downloadImg(itemUrl)
                        sendItem(imgPath)
                        continue
                    if itemType == 2:
                        itemUrl = item['video_versions'][0]['url']
                        sendItem(itemUrl)
                        continue
                print('[+] Sent all feeds to instagram group...')
            else:
                print('[+] No new feeds found...')
            print('[+] Sleeping for 10 minutes before checking the feed again...')
            time.sleep(590)
    except KeyboardInterrupt:
        print('[+] Quiting bot... Please wait...')


# ##############################################< Start execution >##############################################


if __name__ == "__main__":
    main()
