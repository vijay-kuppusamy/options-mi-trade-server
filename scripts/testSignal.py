from django.contrib.auth.models import User
from base.models import ScripMaster, TradingPrice


def run():
    try:
        print("Test Run")

        symbol = "NIFTY"
        user = User.objects.get(pk=3)

        def getScripMaster(symbol):
            try:
                scripMaster = ScripMaster.objects.filter(symbol=symbol).first()
                return scripMaster
            except Exception as e:
                print(e. e.__traceback__)
        # End getScripMaster

        scripMaster = getScripMaster(symbol)
        token = scripMaster.token.strip()
        exch_seg = scripMaster.exch_seg.strip()

        print("token : {} and exch {}".format(token, exch_seg))

        updated_values = {"symboltoken": token,
                          "exch_seg": exch_seg, "price": 0}
        obj, created = TradingPrice.objects.update_or_create(
            user=user, symbol=symbol, defaults=updated_values
        )

        print("Test End")
        
    except Exception as e:
        print(e)
