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


opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())

def request(url,reqbody) :

    req = urllib.request.Request(
        url,
        reqbody,
        method="POST",
        headers={"Content-Type": "application/json"},
    )

#with urllib.request.urlopen(req) as res:
#    print(json.loads(res.read()))
    #response = urllib.request.urlopen(req)
    response = opener.open(req)

    #headers = response.info()
    #print(headers)

    res = response.read()

    response.close()

    return res


load_dotenv()



weburl = os.getenv("WEBURL")
url = os.getenv("URL")

bgtime = 0
bgtimeout = int(os.getenv("BGTIMEOUT"))
sleeptime = int(os.getenv("SLEEPTIME"))

sendwebtimeout = 60*5
sendwebtime = 0

el = 0

try :

    cam=MyCamera(os.getenv("CAMERA_SRV"))

    while True :

        frame=cam.getframe()

        if frame is None : raise Exception

        _,jpeg= cv2.imencode(".jpg", frame)

        ###reqbody=jpeg.tobytes()

        #f = open("sample/sample2.jpg", "rb")
        #reqbody = f.read()
        #f.close()

        t = time.time()

        reqbody = {}
        reqbody["bg"]=False

        if bgtime==0 or (t-bgtime > bgtimeout) :
            reqbody["bg"]=True
            bgtime= time.time()

        imgstr = base64.b64encode(jpeg.tostring()).decode("utf-8")

        reqbody["img"]=imgstr

        res = request(url,json.dumps(reqbody).encode("utf-8"))

        j=json.loads(res)

        if j["res"]>0 :

            img = base64.b64decode(j["img"])

            tm = datetime.datetime.fromtimestamp(t)

            try:
                f = open("{0}/{1}.jpg".format("save",tm.strftime("%Y%m%d%H%M%S")), "wb")
                f.write(img)

            except :
                raise Exception

            finally :
                f.close()



        if sendwebtimeout>0 and (t-sendwebtime > sendwebtimeout) :
            
            sendwebtime = t
            tm = datetime.datetime.fromtimestamp(t)
            reqbody = {}
            reqbody["time"]=tm.strftime("%Y%m%d%H%M%S")
            reqbody["img"]=imgstr
            res = request(weburl,json.dumps(reqbody).encode("utf-8"))
            j = json.loads(res)

            if j["rcode"]=="000" :
                print(j["tm"])
            else :
                print(j["rcode"])

        time.sleep(sleeptime)

except KeyboardInterrupt as e :
    print("exit")
except :
    el=1
    traceback.print_exc()

finally:
    sys.exit(el)
