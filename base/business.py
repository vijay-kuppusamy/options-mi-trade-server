import json
from django.forms.models import model_to_dict

from base.models import Strategy, ExpiryDate, Underlying


class Algo:
    def __init__(self):
        self.underlyingPriceAtBuy = 0
        self.underlyingPrice = 0
        self.ovelallPl = 0
        self.ovelallPlAmt = 0
        self.ovelallPlPct = 0
        self.hasSLhit = False
        self.trailSL = False
        self.positionCount = 0
        self.closedPositions = 0
        self.status = None
        self.complate = False

    def setPositionCount(self, count):
        self.positionCount = count

    def updateOverallPl(self, pl):
        self.ovelallPl = self.ovelallPl + pl

    def updateOverallPlAmt(self, amt):
        self.ovelallPlAmt = self.ovelallPlAmt + amt

    def updateClosedPositions(self):
        self.closedPositions = self.closedPositions + 1
# End class Algo


class PositionStatus:
    def __init__(self):
        self.pl = 0
        self.plAmt = 0
        self.plPct = 0
        self.status = None
        self.hasSLhit = False
# End Class PositionStatus


def getNearestStrike(spotPrice, stepValue):
    return round(spotPrice / stepValue) * stepValue


def getPositionStrikePrice(option, atmStrikePrice, strike, stepValue):
    # sample strike value OTM4, ITM4
    moneyness = strike[:3]
    steps = strike[3:]
    positionStrike = None

    if option == "CE" and moneyness == "OTM":
        positionStrike = atmStrikePrice + (stepValue * int(steps))
    elif option == "CE" and moneyness == "ITM":
        positionStrike = atmStrikePrice - (stepValue * int(steps))
    elif option == "PE" and moneyness == "OTM":
        positionStrike = atmStrikePrice - (stepValue * int(steps))
    elif option == "PE" and moneyness == "ITM":
        positionStrike = atmStrikePrice + (stepValue * int(steps))

    return int(positionStrike)


def getUnderlying(symbol):
    try:
        underlying = Underlying.objects.filter(symbol=symbol).first()
        return underlying
    except Exception as e:
        print(e)


def getExpiryDates(symbol):
    dates = ExpiryDate.objects.filter(
        symbol=symbol).order_by('expirydate').values()
    return dates


def getStrategySettings(name):
    try:
        result = Strategy.objects.filter(name="short_strangle")
        strategy = model_to_dict(result.first())
        settings = json.loads(strategy["settings"])
        return settings
    except Exception as e:
        print(e)
        return None


# def loadPositions(settings):
#     positions = []

#     if settings:
#         try:
#             strategyName = settings['strategyName']
#             underlyingSymbol = settings['underlying']
#             expiry = settings['expiry']
#             rawPositions = settings['positions']

#             # TODO
#             spotprice = 18045
#             underlying = Underlying(underlyingSymbol, 50, 50)
#             #

#             dates = getExpiryDates("NIFTY")
#             expiryDate = dates[int(expiry)]["expirydate"]
#             expiryDateStr = expiryDate.strftime("%d%b%y").upper()

#             atmStrikePrice = getNearestStrike(spotprice, underlying.stepValue)

#             index = 0
#             for position in rawPositions:
#                 option = position['option']
#                 transaction = position['transaction']
#                 strike = position['strike']
#                 noOfLots = position['noOfLots']

#                 positionStrike = getPositionStrikePrice(option,
#                                                         atmStrikePrice, strike, underlying.stepValue)

#                 # NIFTY25JAN2316950PE
#                 symbol = underlyingSymbol+expiryDateStr + \
#                     str(positionStrike) + option

#                 # TODO
#                 premium = 50

#                 position = Position(index, underlyingSymbol, symbol, premium, positionStrike,
#                                     spotprice, option, transaction, expiryDate, noOfLots, underlying.lotSize)
#                 positions.append(position)
#                 index = index+1

#             return positions

#         except Exception as e:
#             print(e)

#     else:
#         return positions
