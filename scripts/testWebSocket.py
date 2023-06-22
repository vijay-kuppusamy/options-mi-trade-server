from django.contrib.auth.models import User

from broker.angeloneWebSocket import SmartWebSocket
from base.models import TradingPrice, ScripMaster


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


def run():
    try:
        print("Start Websocket test")
        user = User.objects.get(pk=2)

        updateSymbolForFeed(user, "NIFTY")
        updateSymbolForFeed(user, "BANKNIFTY")

        task = "mw"
        CLIENT_CODE = user.username
        FEED_TOKEN = user.tradingsession.feedToken
        ss = SmartWebSocket(FEED_TOKEN, CLIENT_CODE, user)

        def process_message(message):
            # message type is list
            print("process message")
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

        print("End Websocket test")
    except Exception as e:
        print(e)
# End run
