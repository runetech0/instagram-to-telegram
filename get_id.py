
from telethon import TelegramClient, events, errors
import logging
import socks
import conf
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)


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
            client = TelegramClient('anon', api_id, api_hash, proxy=sockProxy)
            print(f"[+] Proxy enabled with authentication\n[+] Proxy Server: {conf.SOCKS5_SERVER}:{conf.SOCKS5_PORT}")
    elif not conf.AUTHENTICATION:
        client = TelegramClient('anon', api_id, api_hash, proxy=(socks.SOCKS5, conf.SOCKS5_SERVER, conf.SOCKS5_PORT))
        print(f"[+] Proxy enabled without authentication\n[+] Proxy Server: {conf.SOCKS5_SERVER}:{conf.SOCKS5_PORT}")
else:
    print("[+] Proxy disabled")
    client = TelegramClient('anon', api_id, api_hash)


try:
    while True:
        print("[+] Please Select the channel type using number. CTRL+c : quit.\n[1] Public Channel\n[2] Private/Public Group + Private Channel")
        s = input("[+] Enter 1 or 2: ")
        if int(s) == (1):
            public = True
            guideMsg = "[+] Goto the public channel and forward a message from that channel.\n"
            break
        elif int(s) == 2:
            public = False
            guideMsg = "[+] Goto the channel you want to get id for and send a message!\n"
            break
        else:
            print("[-] Invalid selection. Please Try again!\n")
            continue
except KeyboardInterrupt:
    print("\nQuiting ...\n")
    quit()


@client.on(events.NewMessage())
async def newMessageHandler(msg):
    if public:
        try:
            if msg.fwd_from.channel_id:
                print("-------------------------------------------------------------")
                print("[+] Forwarded message is: {msg.raw_text}")
                print("\n[+] Chat id for public channel is: {msg.fwd_from.channel_id}\n")
                print("-------------------------------------------------------------\n")
        except AttributeError:
            pass
    else:
        try:
            if msg.chat_id:
                print("---------------------------------------------------")
                print("[+] Sent message is: {msg.raw_text}")
                print("\n[+] The chat id for the channel is: {msg.chat_id}")
                print("--------------------------------------------------\n")
        except AttributeError:
            pass


try:
    client.start()
    print(guideMsg)
    client.run_until_disconnected()
except errors.rpcerrorlist.ApiIdInvalidError:
    print("Invalid API_ID/API_HASH")
except KeyboardInterrupt:
    print("\nQuiting ...")
