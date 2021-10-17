'''
This is a demo program which implements ACRCloud Identify Protocol V1 with the third party library "requests".
We recomment you implement your own app with "requests" too.
You can install this python library by:
1) sudo easy_install requests
2) sudo pip install requests
'''

import sys
import os
import base64
import hmac
import hashlib
import time
import requests
import json

'''
Replace "###...###" below with your project's host, access_key and access_secret.
'''
access_key = ""
access_secret = b""
requrl = "http://identify-eu-west-1.acrcloud.com/v1/identify"

http_method = "POST"
http_uri = "/v1/identify"
# default is "fingerprint", it's for recognizing fingerprint, if you want to identify audio, please change data_type="audio"
data_type = "audio"
signature_version = "1"
timestamp = time.time()

string_to_sign = http_method + "\n" + http_uri + "\n" + access_key + "\n" + data_type + "\n" + signature_version + "\n" + str(
    timestamp)

sign = base64.b64encode(hmac.new(access_secret, string_to_sign.encode('utf-8'), digestmod=hashlib.sha1).digest())


# suported file formats: mp3,wav,wma,amr,ogg, ape,acc,spx,m4a,mp4,FLAC, etc
# File size: < 1M , You'de better cut large file to small file, within 15 seconds data size is better
# f = open(sys.argv[1], "rb")
# sample_bytes = os.path.getsize(sys.argv[1])

def check_video(filename):
    files = [
        ('sample', ('test.mp3', open(filename, 'rb'), 'audio/mpeg'))
    ]
    data = {'access_key': access_key,
            'sample_bytes': 44100,
            'timestamp': str(timestamp),
            'signature': sign,
            'data_type': data_type,
            "signature_version": signature_version}

    r = requests.post(requrl, files=files, data=data)
    r.encoding = "utf-8"
    result_dict = r.json()
    print('Checking copyright for audio...')
    if result_dict['status']['code'] == 1001:
        print('Seems unprotected')
        return True
    else:
        print('Protected')
