import requests
import pandas as pd
from base.models import Underlying

FO_MKTLOTS_URL = "https://archives.nseindia.com/content/fo/fo_mktlots.csv"
QTY_FREEZE_URL = "https://archives.nseindia.com/content/fo/qtyfreeze.xls"
SOS_SCHEME = "https://archives.nseindia.com/content/fo/sos_scheme.xls"


def updateSosScheme(symbol, stepValue):
    try:
        obj = Underlying.objects.filter(symbol=symbol).first()
        obj.stepValue = stepValue
        obj.save()
    except Exception as e:
        print(e)


def run():
    print("running script")
    try:
        print("Deleting all the records")
        Underlying.objects.all().delete()
        print("Deleted all the records")

        mktlots = pd.read_csv(FO_MKTLOTS_URL)
        length = len(mktlots)
        print(length)

        for index in range(0, length, 1):
            if index != 4:
                underlyingType = "company"
                if index < 4:
                    underlyingType = "index"

                underlying = mktlots.iloc[index, 0]
                symbol = mktlots.iloc[index, 1]
                lotSize = mktlots.iloc[index, 2]
                try:
                    obj = Underlying.objects.create(
                        underlying=underlying, symbol=symbol, underlyingType=underlyingType, lotSize=lotSize)
                    print("symbol")
                except Exception as e:
                    print(e)

        print("loading qtyfreeze")

        qtyFreeze = pd.read_excel(QTY_FREEZE_URL)
        length = len(qtyFreeze)
        print(type(qtyFreeze))
        print(length)
        # print(qtyFreeze)

        for qtyIndex in range(0, length, 1):
            symbol = qtyFreeze.iloc[qtyIndex, 1]
            qty = qtyFreeze.iloc[qtyIndex, 2]
            try:
                obj = Underlying.objects.filter(symbol=symbol).first()
                obj.qtyFrezze = qty
                obj.save()
            except Exception as e:
                print(e)

            print(symbol)
            print(qty)

        print("loading sos scheme")

        sosScheme = pd.read_excel(SOS_SCHEME)
        length = len(sosScheme)
        print(type(sosScheme))
        print(length)

        for sosIndex in range(0, length, 1):
            symbol = sosScheme.iloc[sosIndex, 0]
            stepValue = sosScheme.iloc[sosIndex, 1]
            updateSosScheme(symbol, stepValue)
            print(symbol)

        updateSosScheme("NIFTY", 50)
        updateSosScheme("BANKNIFTY", 100)
        updateSosScheme("FINNIFTY", 100)
        updateSosScheme("MIDCPNIFTY", 100)

    except Exception as e:
        print(e)

    print("script exiting")
