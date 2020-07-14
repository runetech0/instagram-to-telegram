from configparser import ConfigParser
import requests
import os
import socks
import time
from instagram_private_api import Client, errors as instaErrors
from telethon import TelegramClient, errors
from datetime import datetime as dt
import datetime
from MyClient import getCookie


config = ConfigParser()
config.read('conf.ini')

# ##############################################< Instagram API setup >##############################################

user_name = config['INSTAGRAM']['username']
password = config['INSTAGRAM']['password']

target_username = config['INSTAGRAM']['target_username']


instaCookie = getCookie(user_name, password)

instaClient = Client(user_name, password, cookie=instaCookie)
# print(instaClient.settings)


feedWaitTime = 590

# ##############################################< Telegram Client Setup >##############################################

api_id = config['TELEGRAM']['api_id']
api_hash = config['TELEGRAM']['api_hash']
target_group = config['TELEGRAM'].getint('telegram_destination_group_id')
session_file = 'telegramBot'


# ##############################################< Proxy >##############################################
try:
    proxy_enabled = config['PROXY'].getboolean('enable')
    proxy_server = config['PROXY']['server'].encode()
    proxy_port = config['PROXY'].getint('port')
except KeyError:
    proxy_enabled = True
    proxy_server = '159.89.49.60'
    proxy_port = 31264
    pass


# if config['proxy']['enable']:
#     sockProxy = {
#         "proxy_type": socks.SOCKS5,
#         "addr": conf.SOCKS5_SERVER,
#         "port": conf.SOCKS5_PORT,
#         "rdns": True,
#         "username": conf.USERNAME,
#         "password": conf.PASSWORD
#     }


if proxy_enabled:
    # print(f'Using proxy server {proxy_server}:{proxy_port}')
    telegramClient = TelegramClient(session_file, api_id, api_hash, proxy=(
        socks.SOCKS5, proxy_server, proxy_port))
else:
    telegramClient = TelegramClient(session_file, api_id, api_hash)


# telegramClient = TelegramClient(session_file, api_id, api_hash)

# ##############################################< Helper functions >##############################################


def createTimestamp(sec=0, mins=0, hours=0, days=0):
    now = dt.now() - datetime.timedelta(seconds=sec, minutes=mins, hours=hours, days=days)
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
            try:
                userfeed = instaClient.username_feed(target_username, min_timestamp=createTimestamp(days=100))
            except instaErrors.ClientCheckpointRequiredError:
                print('[-] Instagram has detected bot behaviour...')
                print('[-] Bot is going to sleep... Please login using the browser then restart bot...')
                try:
                    time.sleep(6000)
                    exit()
                    print('[-] Quiting bot...')
                except KeyboardInterrupt:
                    print('[-] Quiting bot...')
                    exit()

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
            print(f'[+] Waiting for {feedWaitTime} Seconds before checking the feed again...')
            time.sleep(feedWaitTime)
    except KeyboardInterrupt:
        print('[+] Quiting bot... Please wait...')
        exit()


# ##############################################< Start execution >##############################################


if __name__ == "__main__":
    print('[+] Starting the bot...')
    try:
        main()
    except KeyboardInterrupt:
        print('[+] Quiting bot...')
        exit()
