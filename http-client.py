import os
import sys
import json
import urllib.parse
import urllib.request
import time
import datetime
import base64
import traceback
from dotenv import load_dotenv

#url = "http://localhost:5000/predict"
#f = open("sample/20210314120359_1.jpg", "rb")


def request(url,reqbody) :

    req = urllib.request.Request(
        url,
        reqbody,
        method="POST",
        headers={"Content-Type": "application/octet-stream"},
    )

#with urllib.request.urlopen(req) as res:
#    print(json.loads(res.read()))
    response = urllib.request.urlopen(req)

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
    while True :

        f = open("sample/sample2.jpg", "rb")
        reqbody = f.read()
        f.close()

        t = time.time()

        if bgtime==0 or (t-bgtime > bgtimeout) :
            res = request(bgurl,reqbody)
            j=json.loads(res)

            bgtime= time.time()

            print("bg\n")

        else :
            res = request(url,reqbody)

            j=json.loads(res)

            if j["res"]>=0 :

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
