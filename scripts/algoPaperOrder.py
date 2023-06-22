import ast
import time
from datetime import datetime
from munch import DefaultMunch
from smartapi import SmartConnect

from base.models import ScripMaster, TradingPrice, SubscribeSymbol
from base.models import Strategy, AlgoOrder, AlgoPosition
from base.utils import getDateTime
from base.business import Algo, PositionStatus
from base.business import getExpiryDates, getUnderlying
from base.business import getPositionStrikePrice

producttype = {"MIS": "INTRADAY", "NRML": "CARRYFORWARD", "CNC": "DELIVERY"}


def getNiftyNearestStrike(spotPrice, stepValue):
    return int(round(spotPrice/(stepValue*2))*(stepValue*2))


def getNearestStrike(spotPrice, stepValue):
    return int(round(spotPrice/stepValue) * stepValue)


def getSmartConnect(user):
    api_key = user.tradingsession.apikey
    access_token = user.tradingsession.jwtToken
    refresh_token = user.tradingsession.refreshToken
    feed_token = user.tradingsession.feedToken

    smartConnect = SmartConnect(api_key=api_key, access_token=access_token,
                                refresh_token=refresh_token, feed_token=feed_token)
    return smartConnect
# End getSmartConnect


def getExpiryDateStr(symbol, expiry):
    dates = getExpiryDates(symbol)
    expiryDate = dates[int(expiry)]["expirydate"]
    expiryDateStr = expiryDate.strftime("%d%b%y").upper()
    return expiryDateStr
# End getExpiryDateStr


def getScripMaster(symbol):
    try:
        scripMaster = ScripMaster.objects.filter(symbol=symbol).first()
        return scripMaster
    except Exception as e:
        print(e. e.__traceback__)
# End getScripMaster


def getLtp(symbol):
    try:
        priceObj = TradingPrice.objects.filter(symbol=symbol).values().first()
        if priceObj is not None:
            return priceObj["price"]
        else:
            return 0
    except Exception as e:
        print(e. e.__traceback__)

    return 0
# End getLtp


def getApiLtp(user, symbol):
    try:
        print("At Get LTP Symbol {}".format(symbol))
        scripMaster = getScripMaster(symbol)
        token = scripMaster.token
        exch_seg = scripMaster.exch_seg

        smartConnect = getSmartConnect(user)
        response = smartConnect.ltpData(
            exchange=exch_seg, tradingsymbol=symbol, symboltoken=token, )

        if response is not None and response['message'] == "SUCCESS":
            ltp = response['data']['ltp']
            return ltp
        else:
            return 0
    except Exception as e:
        print(e. e.__traceback__)

    return 0
# End getLtp


def updateLtp(user, symbol):
    try:
        scripMaster = getScripMaster(symbol)
        token = scripMaster.token.strip()
        exch_seg = scripMaster.exch_seg.strip()

        smartConnect = getSmartConnect(user)
        response = smartConnect.ltpData(
            exchange=exch_seg, tradingsymbol=symbol, symboltoken=token, )

        if response is not None and response['message'] == "SUCCESS":
            ltp = response['data']['ltp']

            obj = TradingPrice.objects.filter(user=user, symbol=symbol).first()
            if obj is not None:
                obj.price = ltp
                obj.save()

    except Exception as e:
        print(e. e.__traceback__)


def updateSymbolForFeed(user, symbol):
    try:
        print("Start updateSymbolForFeed")
        scripMaster = getScripMaster(symbol)
        token = scripMaster.token.strip()
        exch_seg = scripMaster.exch_seg.strip()

        print("token : {} and exch {}".format(token, exch_seg))

        updated_values = {"symboltoken": token,
                          "exch_seg": exch_seg, "price": 0}
        obj, created = TradingPrice.objects.update_or_create(
            user=user, symbol=symbol, defaults=updated_values
        )
        print("updated TradingPrice")
        subscribe = SubscribeSymbol.objects.create(
            user=user, symboltoken=token, exch_seg=exch_seg)
        print("end updateSymbolForFeed")
    except Exception as e:
        print(e. e.__traceback__)

# End updateSymbolForFeed


def loadAlgoPositions(user, algoOrder, strategySettings, atmStrikePrice, expiryDateStr, underlying):
    print("Start loadAlgoPositions")
    positions = []
    try:
        dictPositions = ast.literal_eval(algoOrder.positions)
        for rawPosition in dictPositions:
            position = getAlgoPosition(
                user, algoOrder, strategySettings, rawPosition, atmStrikePrice, expiryDateStr, underlying)
            positions.append(position)
    except Exception as e:
        print(e. e.__traceback__)

    print("End loadAlgoPositions")
    return positions
# End loadAlgoPositions


def getAlgoPosition(user, algoOrder, strategySettings, dictPosition, atmStrikePrice, expiryDateStr, underlying,):
    print("Start getAlgoPosition")
    try:
        position = DefaultMunch.fromDict(dictPosition)
        option = position.option
        strike = position.strike.value

        print("option : {} and strike : {}".format(option, strike))

        positionStrike = getPositionStrikePrice(
            option, atmStrikePrice, strike, underlying.stepValue)

        # NIFTY25JAN2316950PE
        print(underlying.symbol)
        symbol = (underlying.symbol.strip() + expiryDateStr +
                  str(positionStrike) + option).upper()
        print(symbol)

        updateSymbolForFeed(user, symbol)
        # if websocket is not running call this line, just to test
        # updateLtp(user, symbol)

        scripMaster = getScripMaster(symbol)
        token = scripMaster.token.strip()
        exch_seg = scripMaster.exch_seg.strip()

        algoPosition = AlgoPosition.objects.create(order=algoOrder)

        algoPosition.symbol = symbol
        algoPosition.symboltoken = token
        algoPosition.exch_seg = exch_seg
        algoPosition.option = option
        algoPosition.quantity = int(
            position.lots.value) * int(underlying.lotSize)
        algoPosition.ordertype = "MARKET"
        algoPosition.producttype = producttype[strategySettings.product]
        algoPosition.transaction = position.transaction.upper()

        algoPosition.target = position.target
        algoPosition.targetType = position.targetType.value
        algoPosition.targetValue = int(position.targetValue)
        algoPosition.stoploss = position.stoploss
        algoPosition.stoplossType = position.stoplossType.value
        algoPosition.stoplossValue = int(position.stoplossValue)
        algoPosition.trailSL = position.trailSL
        algoPosition.trailSLType = position.trailSLType.value
        algoPosition.trailSLValue = int(position.trailSLValue)

        algoPosition.status = "open"
        algoPosition.save()
        print("End getAlgoPosition")
        return algoPosition

    except Exception as e:
        print(e. e.__traceback__)

    print("End getAlgoPosition return none")
    return None
# End getAlgoPosition


def calculatePL(position, ltp):
    pl = 0
    if position.transaction == "BUY":
        return float(position.buyPrice) - float(ltp)
    elif position.transaction == "SELL":
        return float(ltp) - float(position.buyPrice)
    return pl
# End calculatePL


def calculatePositionPL(user, position, algo):
    symbol = position.symbol
    positionStatus = PositionStatus()
    pl = 0
    plAmt = 0
    plPct = 0

    if position.status == "open":
        ltp = getLtp(symbol)
        if ltp > 0:
            pl = calculatePL(position, ltp)
            plAmt = pl * position.quantity
            plPct = (100 * pl) / position.buyPrice
            if position.stoploss:
                value = 0
                if position.stoplossType == "Percentage":
                    value = plPct
                elif position.stoplossType == "Points":
                    value = pl

                if value < 0 and abs(value) > position.stoplossValue:
                    positionStatus.hasSLhit = True
                    algo.trailSL = True
                    position.status = "closed"
                    ltp = getApiLtp(user, symbol)
                    position.sellPrice = ltp
                    position.save()
                # End if
            # End if stoploss
            if position.trailSL and algo.trailSL:

                if position.trailPrice <= 0:
                    position.trailPrice = ltp
                if position.transaction == "BUY" and ltp > position.trailPrice:
                    position.trailPrice = ltp
                if position.transaction == "SELL" and ltp < position.trailPrice:
                    position.trailPrice = ltp

                trail_chg = 0
                trail_chg_pct = 0
                if position.transaction == "BUY":
                    trail_chg = ltp - position.trailPrice
                if position.transaction == "SELL":
                    trail_chg = position.trailPrice - ltp

                trail_chg_pct = (100 * trail_chg) / position.trailPrice

                value = 0
                if position.trailSLType == "Percentage":
                    value = trail_chg_pct
                elif position.trailSLType == "Points":
                    value = trail_chg

                if trail_chg < 0 and abs(trail_chg) >= value:
                    print("trail stop loss hit")
                    position.status = "closed"
                    ltp = getApiLtp(user, symbol)
                    position.sellPrice = ltp
                    position.save()
                # End if
            # End if trailSL
        # End if ltp > 0
    # End if status open
    elif position.status == "closed":
        pl = calculatePL(position, position.sellPrice)
        plAmt = pl * position.quantity
        plPct = (100 * pl) / position.buyPrice
    # End if status closed

    print("PL {}, PL Amt {}, PL Pct {} ".format(pl, plAmt, plPct))
    positionStatus.pl = pl
    positionStatus.plAmt = plAmt
    positionStatus.plPct = plPct
    return position, positionStatus, algo
# End calculatePositionPL


def run():
    try:
        print("Start Algo Paper Order Script")

        # Update order id
        orderid = 1
        algoOrder = AlgoOrder.objects.get(pk=orderid)

        user = algoOrder.user
        settings = ast.literal_eval(algoOrder.settings)
        strategySettings = DefaultMunch.fromDict(settings)
        print("Got Strategy Settings ")

        underlyingSymbol = strategySettings.underlying.value
        expiry = strategySettings.expiry.value

        updateSymbolForFeed(user, underlyingSymbol)
        # if websocket is not running call this line, just to test
        # updateLtp(user, underlyingSymbol)

        underlying = getUnderlying(underlyingSymbol)
        expiryDateStr = getExpiryDateStr(underlyingSymbol, expiry)
        print("underlying : {}".format(underlying))
        print("expiryDateStr : {}".format(expiryDateStr))

        # TODO
        start_time = "11:37"
        end_time = "11:45"
        start_time = getDateTime(start_time)
        end_time = getDateTime(end_time)
        # uncomment the line below and remove above
        # start_time = getDateTime(strategySettings.entryTime)
        # end_time = getDateTime(strategySettings.exitTime)
        print(start_time)

        algoPositions = []
        algo = Algo()
        algo.status = "Pending"
        algo.complete = False

        while not algo.complete:

            now = datetime.now()
            if algo.status == "Pending" and now.time() >= start_time.time():
                algo.status = "Create"
            # Start Time Check
            if algo.status == "Running" and now.time() >= end_time.time():
                algo.status = "Close"
            # End Time Check

            print("Status {} at {}".format(algo.status, now))
            match algo.status:
                case "Pending":
                    pass
                # End Status Pending

                case "Create":
                    # creating positions
                    spotprice = getLtp(underlyingSymbol)
                    print("spotprice : {}".format(spotprice))
                    if spotprice is not None and spotprice > 0:
                        atmStrikePrice = None
                        if underlyingSymbol == "NIFTY":
                            print("spot price : {} and stepvalue {}".format(
                                spotprice, underlying.stepValue))
                            atmStrikePrice = getNiftyNearestStrike(
                                spotprice, underlying.stepValue)
                        else:
                            atmStrikePrice = getNearestStrike(
                                spotprice, underlying.stepValue)

                        print("atmStrikePrice : {}".format(atmStrikePrice))

                        algoPositions = loadAlgoPositions(
                            user, algoOrder, strategySettings, atmStrikePrice, expiryDateStr, underlying)

                        algo.status = "Start"
                    # end if : spot price check
                # End Status Create

                case "Start":
                    algoPositions = list(AlgoPosition.objects.filter(
                        order=algoOrder))
                    for position in algoPositions:
                        ltp = getApiLtp(user, position.symbol)
                        print(ltp)
                        position.buyPrice = ltp
                        position.save()
                        print("save")
                    algo.status = "Running"
                # End Status Start

                case "Running":
                    algoPositions = list(AlgoPosition.objects.filter(
                        order=algoOrder))
                    # set the overall algo  profit to zero
                    for index, algoPosition in enumerate(algoPositions):

                        position, positionStatus, returnAlgo = calculatePositionPL(
                            user, algoPosition, algo)
                        algoPositions[index] = position
                        algo = returnAlgo
                        # Overall algo PL calculations
                    # Check algo level SL
                # End Status Running

                case "Close":
                    # check the positions
                    print("close")
                    positions = list(
                        AlgoPosition.objects.filter(order=algoOrder))
                    for index, position in enumerate(positions):
                        print("inside for")
                        if position.status == "open":
                            print("inside if")
                            ltp = getApiLtp(user, position.symbol)
                            position.sellPrice = ltp
                            position.status = "closed"
                            position.save()
                            positions[index] = position
                    # End for
                    algo.status = "End"
                    print(algo.status)
                # End Status Close

                case "End":
                    algo.complete = True
                # End Status End
            # End match

            time.sleep(1)
        # End While

        print(algo.status)

    except Exception as e:
        print("Error in Algo Paper Order Script : ", e, e.__traceback__)

    print("End Algo Paper Order Script")
# End run
