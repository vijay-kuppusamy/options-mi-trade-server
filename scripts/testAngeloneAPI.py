from django.contrib.auth.models import User
from base.models import ScripMaster
from smartapi import SmartConnect


def getScripMaster(symbol):
    try:
        scripMaster = ScripMaster.objects.filter(
            symbol=symbol).values().first()
        return scripMaster
    except Exception as e:
        print(e)


def run():
    try:
        print("Test API")
        user = User.objects.get(pk=6)
        api_key = user.tradingsession.apikey
        access_token = user.tradingsession.jwtToken
        refresh_token = user.tradingsession.refreshToken
        feed_token = user.tradingsession.feedToken

        connection = SmartConnect(api_key=api_key, access_token=access_token,
                                  refresh_token=refresh_token, feed_token=feed_token)

        symbol = "NIFTY"
        # symbol = "SBIN-EQ"
        scripMaster = getScripMaster(symbol)
        token = scripMaster["token"]
        exch_seg = scripMaster["exch_seg"]

        print(symbol)
        print(token)
        print(exch_seg)

        response = connection.ltpData(
            exchange=exch_seg, tradingsymbol=symbol, symboltoken=token, )

        print(type(response))
        print(response['message'])
        print(response['data']['tradingsymbol'])
        print(response['data']['ltp'])

        # historicParam = {
        #     "exchange": exch_seg,
        #     "symboltoken": token,
        #     "interval": "ONE_MINUTE",
        #     "fromdate": "2022-12-16 09:15",
        #     "todate": "2022-12-16 09:20"
        # }
        # response = connection.getCandleData(historicParam)
        # print(response)

    except Exception as e:
        print(e)
