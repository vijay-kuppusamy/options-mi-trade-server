from datetime import datetime
from base.models import ScripMaster, ExpiryDate, StrikePrice

monthsDic = {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
             "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12, }


def run():
    try:

        scrips = ScripMaster.objects.filter(
            name="NIFTY", exch_seg="NFO").values()

        print(len(scrips))
        expiryDates = set()
        strikePrices = set()

        # "NIFTY25JAN2316950PE"
        for scrip in scrips:
            text = scrip["symbol"]
            expiryDateStr = text[5:12]
            eDate = expiryDateStr[:2]
            eMonth = expiryDateStr[2:5]
            eYear = expiryDateStr[5:]
            expiryDate = datetime(
                int("20"+eYear), monthsDic[eMonth], int(eDate))

            expiryDates.add(expiryDate)

            strikePrice = text[12:]
            strikePrice = strikePrice[:-2]

            strikePrices.add(expiryDateStr+strikePrice)

        print("Deleting Expiry Dates")
        ExpiryDate.objects.all().delete()
        print("Deleted Expiry Dates")
        for date in expiryDates:
            print(date)
            try:
                obj = ExpiryDate.objects.create(
                    symbol="NIFTY", expirydate=date)
                obj.save()
            except Exception as e:
                print(e)

        print("Expiry Dates Saved")
        # 25JAN2316950
        # print(strikePrices)
        print("Deleting Strike Prices")
        StrikePrice.objects.all().delete()
        print("Deleted Strike Prices")
        for price in strikePrices:
            print(price)
            expiryDateStr = price[:7]
            eDate = expiryDateStr[:2]
            eMonth = expiryDateStr[2:5]
            eYear = expiryDateStr[5:]
            expiryDate = datetime(
                int("20"+eYear), monthsDic[eMonth], int(eDate))
            print(expiryDate)
            strikePrice = price[7:]

            try:
                obj = StrikePrice.objects.create(
                    symbol="NIFTY", expirydate=expiryDate, price=strikePrice)
                obj.save()
            except Exception as e:
                print(e)

        print("Strike Prices Saved")

    except Exception as e:
        print(e)
