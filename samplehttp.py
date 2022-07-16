import os
import sys
import cv2
import numpy as np
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



bgurl = os.getenv("BGURL")
url = os.getenv("URL")

bgtime = 0
bgtimeout = int(os.getenv("BGTIMEOUT"))
sleeptime = int(os.getenv("SLEEPTIME"))

el = 0

try :

    f = open("sample/sample2.jpg", "rb")
    jpeg = f.read()
    f.close()

    img_buf= np.frombuffer(jpeg, dtype=np.uint8)

    frame = cv2.imdecode(img_buf, flags=cv2.IMREAD_COLOR)

    print(type(frame))

    _,jpeg = cv2.imencode('.jpg', frame)

    imgstr = base64.b64encode(jpeg.tostring()).decode("utf-8")

    reqbody = {}

    reqbody["img"]=imgstr
    reqbody["bg"]=True

#    print(reqbody)

    res = request(url,json.dumps(reqbody).encode("utf-8"))

    print(res)

except KeyboardInterrupt as e :
    print("exit")
except :
    el=1
    traceback.print_exc()

finally:
    sys.exit(el)


'''
try :

    cam=MyCamera(os.getenv("CAMERA_SRV"))

    while True :

        frame=cam.getframe()

        if frame is None : raise Exception

        _,jpeg= cv2.imencode(".jpg", frame)

        reqbody=jpeg.tobytes()

        #f = open("sample/sample2.jpg", "rb")
        #reqbody = f.read()
        #f.close()

        t = time.time()

        if bgtime==0 or (t-bgtime > bgtimeout) :

            res = request(bgurl,reqbody)

            j=json.loads(res)

            bgtime= time.time()

        else :
            res = request(url,reqbody)

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

        time.sleep(sleeptime)

except KeyboardInterrupt as e :
    print("exit")
except :
    el=1
    traceback.print_exc()

finally:
    sys.exit(el)
'''
