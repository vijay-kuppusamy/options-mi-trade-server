from django.contrib.auth.models import User
from django.db.models import signals
from django.dispatch import receiver
from datetime import datetime
from base.utils import getDateTime
import time
import pytz
import logging
from smartapi import SmartWebSocket
from base.models import TradingPrice, ScripMaster, SubscribeSymbol

logger = logging.getLogger("tasks")

def getScripMaster(symbol):
    try:
        scripMaster = ScripMaster.objects.filter(
            symbol=symbol).values().first()
        return scripMaster
    except Exception as e:
        print(e)
# End getScripMaster


def updateSymbolForFeed(user, symbol):
    try:
        scripMaster = getScripMaster(symbol)
        token = scripMaster["token"]
        exch_seg = scripMaster["exch_seg"]

        updated_values = {"symboltoken": token,
                          "exch_seg": exch_seg, "price": 0}
        obj, created = TradingPrice.objects.update_or_create(
            user=user, symbol=symbol, defaults=updated_values
        )

    except Exception as e:
        print(e)
# End updateSymbolForFeed


def updateTradingPrice(user, token, ltp):
    try:
        obj = TradingPrice.objects.filter(user=user, symboltoken=token).first()
        obj.price = ltp
        obj.save()
    except Exception as e:
        print("Error in update trading price : ", e)
# End updateTradingPrice


def constructTokens(symbols):
    token = ""
    if len(symbols) > 0:

        for symbol in symbols:
            symboltoken = symbol["symboltoken"]
            exch_seg = symbol["exch_seg"]
            if exch_seg == "NSE":
                exch_seg = "nse_cm"
            elif exch_seg == "NFO":
                exch_seg = "nse_fo"

            if token == "":
                token = exch_seg + "|" + symboltoken
            else:
                token = token + "&" + exch_seg + "|" + symboltoken

    return token
# End constructTokens


def tradingsession(id):
    try:
        print("Start Websocket test")
        user = User.objects.get(pk=id)

        updateSymbolForFeed(user, "NIFTY")
        updateSymbolForFeed(user, "BANKNIFTY")

        task = "mw"
        CLIENT_CODE = user.username
        FEED_TOKEN = user.tradingsession.feedToken
        ss = SmartWebSocket(FEED_TOKEN, CLIENT_CODE)

        def subscribe_symbol():
            logger.info("Inside subscribe_symbol")
            try:
                request = list(
                    SubscribeSymbol.objects.filter(user=user).values())
                if len(request) > 0:
                    # sub logic
                    tokens = constructTokens(request)
                    ss.subscribe("mw", tokens)
                    SubscribeSymbol.objects.filter(user=user).delete()
                    logger.info("Subscription done ")
            except Exception as e:
                print(e)

        def process_message(message):
            # message type is list
            for tick in message:
                # tick type is dict
                try:
                    name = tick["name"]
                    if name == "sf":
                        token = tick["tk"]
                        ltp = tick["ltp"]
                        updateTradingPrice(user, token, ltp)
                except Exception as e:
                    print("Error in process message ", e)

        def on_message(ws, message):
            process_message(message)
            subscribe_symbol()
            print("Ticks: {}".format(message))

        def on_open(ws):
            print("on open")
            task = "mw"
            token = "nse_cm|26000&nse_cm|26009"
            ss.subscribe(task, token)

        def on_error(ws, error):
            print("on error ", error)

        def on_close(ws):
            print("Close")

        ss._on_open = on_open
        ss._on_message = on_message
        ss._on_error = on_error
        ss._on_close = on_close

        ss.connect()

        # TODO
        # Need to terminate the connection from another task

        # end_time = getDateTime("15:30")
        # marketOpen = True

        # while marketOpen:
        #     now = datetime.now(pytz.timezone("Asia/Kolkata"))
        #     if now.time() >= end_time.time():
        #         marketOpen = False
        #         ss.ws.close()
        #     time.sleep(60)

    except Exception as e:
        print(e)

    return {"status": "success"}
# End tradingsession
