import time
from datetime import datetime
import threading

from django.contrib.auth.models import User
from base.models import SubscribeSymbol
from base.utils import getDateTime

SLEEP_INTERVAL = 30


def constructTokens(symbols):
    token = ""
    if len(symbols) > 0:

        for symbol in symbols:
            symboltoken = symbol["symboltoken"]
            exch_seg = symbol["exch_seg"]
            if token == "":
                token = exch_seg + "|" + symboltoken
            else:
                token = token + "&" + exch_seg + "|" + symboltoken

    return token


def run():
    try:
        print("Test Run")

        user = User.objects.get(pk=6)

        end_time = getDateTime("12:05")
        complete = False

        while not complete:
            now = datetime.now()
            print(now)
            if now.time() >= end_time.time():
                complete = True

            try:
                request = list(
                    SubscribeSymbol.objects.filter(user=user).values())
                print(len(request))
                if len(request) > 0:
                    # sub logic
                    constructTokens(request)
                    # delete after sub
                    # SubscribeSymbol.objects.all().delete()
                    print("Subscription done ")
            except Exception as e:
                print(e)

            time.sleep(SLEEP_INTERVAL)

        print("Test End")
    except Exception as e:
        print(e)
