import os
import sys
import cv2
import json
import urllib.parse
import urllib.request
import time
import datetime
import base64
import traceback
from dotenv import load_dotenv

from mitsuba.mycam import MyCamera

#url = "http://localhost:5000/predict"
#f = open("sample/20210314120359_1.jpg", "rb")

load_dotenv()

webm2mid = os.getenv("M2M_CLIENT_ID")
webm2msecret = os.getenv("M2M_CLIENT_SECRET")
webauthurl = os.getenv("WEB_AUTH_URL")
webimgposturl = os.getenv("WEB_POSTIMG_URL")
url = os.getenv("URL")



opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())


def request(url,reqbody) :

    req = urllib.request.Request(
        url,
        reqbody,
        method="POST",
        headers={"Content-Type": "application/json"},
    )

    response = opener.open(req)
    res = response.read()
    response.close()

    return res

def getAccessToken() :

    reqbody = {}
    reqbody["clientid"] = webm2mid
    reqbody["clientsecret"] = webm2msecret

    req = urllib.request.Request(
        webauthurl,
        json.dumps(reqbody).encode("utf-8"),
        method="POST",
        headers={"Content-Type": "application/json"},
    )

    response = opener.open(req)

    if response.code!=200 : return None,None

    res = response.read()

    response.close()

    j=json.loads(res)

    if j["rcode"] != "000" : return None,None

    t = time.time() + 10#j["lifetime"]

    return j["access_token"],t

def sendImage(accesstoken,imgstr) :

    reqbody = {}
    reqbody["time"] = ""
    reqbody["img"] = imgstr

    req = urllib.request.Request(
        webimgposturl,
        json.dumps(reqbody).encode("utf-8"),
        method="POST",
        headers={"Content-Type" : "application/json",
                 "Authorization" : "Bearer {0}".format(accesstoken)
        },
    )

    response = opener.open(req)

    if response.code!=200 : return None

    res = response.read()

    response.close()

    j = json.loads(res)

    if j["rcode"] != "000" : return None
 
    return j["rcode"]


accesstoken = None
tokenlifetime = None


bgtime = 0
bgtimeout = int(os.getenv("BGTIMEOUT"))
sleeptime = int(os.getenv("SLEEPTIME"))

savepath = os.getenv("SAVEPATH")

sendwebtimeout = int(os.getenv("SENDWEBTIMEOUT"))
sendwebtime = 0

el = 0

try :

    while True :

        t = time.time()

        f = open("20220828184054.jpg", "rb")
        jpgimg = f.read()
        f.close()

        imgstr = base64.b64encode(jpgimg).decode("utf-8")

        if sendwebtimeout>0 and (t-sendwebtime > sendwebtimeout) :

            sendwebtime = t

            # if acccesstoken is expired
            if (tokenlifetime is None) or (tokenlifetime < t) :
                
                print("get access_token")
                at,limittm = getAccessToken()

                if limittm is None : raise Exception

                accesstoken = at
                tokenlifetime = limittm

            if sendImage(accesstoken,imgstr) is None : raise Exception

        time.sleep(sleeptime)

except KeyboardInterrupt as e :
    print("exit")
except :
    el=1
    traceback.print_exc()

finally:
    sys.exit(el)
