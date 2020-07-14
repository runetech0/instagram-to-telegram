import base64
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_v1_5
import datetime
import requests

from Crypto.PublicKey import RSA


def main(passwd):
    hashed = encpass(passwd)
    print(hashed)
    return hashed


def encpass(passwd):
    password = passwd
    publickeyid, publickey = get_publickey_details("", "")
    session_key = get_random_bytes(32)
    iv = bytearray(12)
    time = str(int(datetime.datetime.now().timestamp()))
    decoded_publickey = base64.b64decode(publickey.encode())
    recipient_key = RSA.import_key(decoded_publickey)
    cipher_rsa = PKCS1_v1_5.new(recipient_key)
    enc_session_key = cipher_rsa.encrypt(session_key)
    cipher_aes = AES.new(session_key, AES.MODE_GCM, iv)
    cipher_aes.update(time.encode())
    ciphertext, tag = cipher_aes.encrypt_and_digest(password.encode("utf8"))
    payload = base64.b64encode((b"\x01\x00" + publickeyid.to_bytes(2, byteorder='big') + iv +
                                len(enc_session_key).to_bytes(2, byteorder='big') + enc_session_key + tag + ciphertext))
    return f"#PWD_INSTAGRAM:4:{time}:{payload.decode()}"


def get_publickey_details(publickeyid, publickey):
    r = requests.get('https://i.instagram.com/api/v1/qe/sync/')
    publickeyid = int(r.headers['ig-set-password-encryption-key-id'])
    publickey = r.headers['ig-set-password-encryption-pub-key']
    return (publickeyid, publickey)


if __name__ == '__main__':
    main('Hello')
