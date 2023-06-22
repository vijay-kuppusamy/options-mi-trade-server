import ast
import time
from datetime import datetime
from munch import DefaultMunch
from smartapi import SmartConnect

from base.models import Strategy, ScripMaster, TradingPrice, SubscribeSymbol
from base.models import AlgoOrder, AlgoPosition
from base.utils import getDateTime, getDateStr
from base.business import Algo, PositionStatus
from base.business import getExpiryDates, getUnderlying
from base.business import getPositionStrikePrice

producttype = {"MIS": "INTRADAY", "NRML": "CARRYFORWARD", "CNC": "DELIVERY"}


def getNiftyNearestStrike(spotPrice, stepValue):
    return round((spotPrice / (stepValue * 2)) * (stepValue * 2))


def getNearestStrike(spotPrice, stepValue):
    return round((spotPrice / stepValue) * stepValue)


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
        scripMaster = ScripMaster.objects.filter(
            symbol=symbol).values().first()
        return scripMaster
    except Exception as e:
        print(e)
# End getScripMaster


def getLtp(symbol):
    try:
        priceObj = TradingPrice.objects.filter(symbol=symbol).values().first()
        if priceObj is not None:
            return priceObj["price"]
        else:
            return 0
    except Exception as e:
        print(e)
    return 0
# End getLtp


def getApiLtp(symbol, smartConnect):
    try:
        scripMaster = getScripMaster(symbol)
        token = scripMaster["token"]
        exch_seg = scripMaster["exch_seg"]

        response = smartConnect.ltpData(
            exchange=exch_seg, tradingsymbol=symbol, symboltoken=token, )

        if response is not None and response['message'] == "SUCCESS":
            ltp = response['data']['ltp']
            return ltp
        else:
            return 0
    except Exception as e:
        print(e)

    return 0
# End getLtp


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

        subscribe = SubscribeSymbol.objects.create(
            user=user, symboltoken=token, exch_seg=exch_seg)

    except Exception as e:
        print(e)
# End updateSymbolForFeed


def loadAlgoPositions(user, algoOrder, strategySettings, atmStrikePrice, expiryDateStr, underlying):
    positions = []
    try:
        dictPositions = ast.literal_eval(algoOrder.positions)
        for rawPosition in dictPositions:
            position = getAlgoPosition(
                user, algoOrder, strategySettings, rawPosition, atmStrikePrice, expiryDateStr, underlying)
            positions.append(position)
    except Exception as e:
        print(e)
    return positions
# End loadAlgoPositions


def placeOrder(user, algoPosition, squareoff):
    try:

        if squareoff and algoPosition.transaction == "BUY":
            transaction = "SELL"
        elif squareoff and algoPosition.transaction == "SELL":
            transaction = "BUY"

        smartConnect = getSmartConnect(user)
        orderparams = {
            "variety": "NORMAL",
            "tradingsymbol": algoPosition.symbol,
            "symboltoken": algoPosition.token,
            "transactiontype": transaction,
            "exchange": algoPosition.exch_seg,
            "ordertype": algoPosition.ordertype,
            "producttype": algoPosition.producttype,
            "duration": "DAY",
            "price": "0",
            "squareoff": "0",
            "stoploss": "0",
            "quantity": algoPosition.quantity,
        }
        buyOrderId = smartConnect.placeOrder(orderparams)
        return buyOrderId
    except Exception as e:
        print(e)
    return None
# End placeOrder


def updateOrderBook(user, position):
    print("update order book")
    smartConnect = getSmartConnect(user)
    orderbook = smartConnect.orderBook()
    updated = False
    if orderbook is not None and orderbook["message"] == "SUCCESS":
        orders = orderbook["data"]
        for order in orders:
            orderid = order["orderid"]
            if position.sellOrderId == orderid:
                price = order["price"]
                position.sellPrice = price
                position.save()
                return position, True
            # End position update
        # End For loop
    # End if orderbook
    return None, updated
# End updateOrderBook


def updateBuyOrderBook(user, algoOrder):
    print("update buy order book")

    smartConnect = getSmartConnect(user)
    orderbook = smartConnect.orderBook()
    if orderbook is not None and orderbook["message"] == "SUCCESS":
        orders = orderbook["data"]
        for order in orders:
            orderid = order["orderid"]
            position = AlgoPosition.objects.filter(
                order=algoOrder, buyOrderId=orderid)
            if position is not None:
                price = order["price"]
                position.buyPrice = price
                position.save()
            # End position update
        # End For loop
        algoPositions = AlgoPosition.objects.filter(order=algoOrder)
        return algoPositions
    # End if orderbook
    return None
# End updateBuyOrderBook


def updateSellOrderBook(user, algoOrder):
    print("update sell order book")

    smartConnect = getSmartConnect(user)
    orderbook = smartConnect.orderBook()
    if orderbook is not None and orderbook["message"] == "SUCCESS":
        orders = orderbook["data"]
        for order in orders:
            orderid = order["orderid"]
            position = AlgoPosition.objects.filter(
                order=algoOrder, sellOrderId=orderid)
            if position is not None:
                price = order["price"]
                position.sellPrice = price
                position.save()
            # End position update
        # End For loop
        algoPositions = AlgoPosition.objects.filter(order=algoOrder)
        return algoPositions
    # End if orderbook
    return None
# End updateSellOrderBook


def getAlgoPosition(user, algoOrder, strategySettings, dictPosition, atmStrikePrice, expiryDateStr, underlying,):
    try:
        position = DefaultMunch.fromDict(dictPosition)
        option = position.option
        strike = position.strike.value

        positionStrike = getPositionStrikePrice(
            option, atmStrikePrice, strike, underlying["stepValue"])

        # NIFTY25JAN2316950PE
        symbol = (underlying["symbol"] + expiryDateStr +
                  str(positionStrike) + option).upper()

        updateSymbolForFeed(user, symbol)

        scripMaster = getScripMaster(symbol)
        token = scripMaster["token"]
        exch_seg = scripMaster["exch_seg"]

        algoPosition = AlgoPosition.objects.create(order=algoOrder)
        print(symbol)
        algoPosition.symbol = symbol
        algoPosition.symboltoken = token
        algoPosition.exch_seg = exch_seg
        algoPosition.option = option
        algoPosition.quantity = int(
            position.lots.value) * int(underlying["lotSize"])
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

        buyOrderId = placeOrder(user, algoPosition, False)
        algoPosition.buyOrderId = buyOrderId
        algoPosition.status = "open"
        algoPosition.save()
        return algoPosition

    except Exception as e:
        print(e)

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
                    orderId = placeOrder(user, position, True)
                    position.sellOrderId = orderId
                    position.status = "closed"
                    updated = False
                    while not updated:
                        position, updated = updateOrderBook(user, position)
                    # End Ehile
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
                    orderId = placeOrder(user, position, True)
                    position.sellOrderId = orderId
                    position.status = "closed"
                    updated = False
                    while not updated:
                        position, updated = updateOrderBook(user, position)
                    # End Ehile
                # End if
            # End if trailSL
        # End if ltp > 0
    # End if status open
    elif position.status == "closed":
        pl = calculatePL(position, position.sellPrice)
        plAmt = pl * position.quantity
        plPct = (100 * pl) / position.buyPrice
    # End if status closed

    positionStatus.pl = pl
    positionStatus.plAmt = plAmt
    positionStatus.plPct = plPct
    return position, positionStatus, algo
# End calculatePositionPL


def run():
    try:
        print("Running Test Script")

        algoOrder = AlgoOrder.objects.get(pk=1)

        user = algoOrder.user
        settings = ast.literal_eval(algoOrder.settings)
        strategySettings = DefaultMunch.fromDict(settings)

        underlyingSymbol = strategySettings.underlying.value
        expiry = strategySettings.expiry.value

        updateSymbolForFeed(user, underlyingSymbol)
        underlying = getUnderlying(underlyingSymbol)
        expiryDateStr = getExpiryDateStr(underlyingSymbol, expiry)
        print(expiryDateStr)

        # TODO
        start_time = "20:02"
        end_time = "20:03"
        start_time = getDateTime(start_time)
        end_time = getDateTime(end_time)
        # uncomment the line below and remove above
        # start_time = getDateTime(strategySettings.entryTime)
        # end_time = getDateTime(strategySettings.exitTime)
        print(start_time)

        smartConnect = getSmartConnect(user)

        algoPositions = []
        algo = Algo()
        algo.status = "Pending"
        algo.complete = False

        while not algo.complete:

            now = datetime.now()
            if algo.status == "Pending" and start_time.time() >= now.time():
                algo.status = "Create"
            # Start Time Check
            if now.time() >= end_time.time():
                algo.status = "Close"
            # End Time Check

            match algo.status:
                case "Pending":
                    print("Pending")
                # End Status Pending

                case "Create":
                    print("Create")
                    # creating positions
                    spotprice = getLtp(underlyingSymbol)
                    if spotprice is not None and spotprice > 0:
                        atmStrikePrice = None
                        if underlyingSymbol == "NIFTY":
                            atmStrikePrice = getNiftyNearestStrike(
                                spotprice, underlying["stepValue"])
                        else:
                            atmStrikePrice = getNearestStrike(
                                spotprice, underlying["stepValue"])

                        print(atmStrikePrice)

                        algoPositions = loadAlgoPositions(
                            user, algoOrder, strategySettings, atmStrikePrice, expiryDateStr, underlying)
                        algo.status = "Start"
                    # end if : spot price check
                # End Status Create

                case "Start":
                    print("Start")
                    positions = updateBuyOrderBook(user, algoOrder)
                    if algoPositions is not None:
                        algoPositions = list(positions)
                    # End if
                    priceUpdated = False
                    for positions in algoPositions:
                        if position.buyPrice > 0:
                            priceUpdated = True
                        else:
                            priceUpdated = False
                    if priceUpdated:
                        algo.status = "Running"
                # End Status Start

                case "Running":
                    print("Running")
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
                    print("Close")
                    # check the positions
                    # close the positions
                    algo.status = "End"
                # End Status Close

                case "End":
                    print("End")
                    # check the order status and update
                    algo.complete = True
                # End Status End
            # End match

            time.sleep(1)
        # End While

        print(algo.status)

    except Exception as e:
        print(e)
    print("Exiting Test Script")
# End run
