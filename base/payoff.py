import math

from .business import getNearestStrike


class Payoff:
    def __init__(self, positions, underlying):
        self.positions = positions
        self.underlying = underlying
        self.priceList = []
        self.profitLossList = []

    def positionProfitLossByPrice(self, position, price):
        pl = 0

        if (position.option == "CE" and position.transaction == "buy"):
            pl = max(0, price - position.strikePrice) - position.premium
        elif (position.option == "CE" and position.transaction == "sell"):
            pl = position.premium - max(0, price - position.strikePrice)
        elif (position.option == "PE" and position.transaction == "buy"):
            pl = max(0, position.strikePrice - price) - position.premium
        elif (position.option == "PE" and position.transaction == "sell"):
            pl = position.premium - max(0, position.strikePrice - price)

        return pl

    def isBetween(self, low, high, value):
        return value >= low and value < high

    def roundVal(self, value):
        if (self.isBetween(0, 10, value)):
            return math.ceil(value / 1) * 1
        elif (self.isBetween(10, 100, value)):
            return math.ceil(value / 10) * 10
        elif (self.isBetween(100, 1000, value)):
            return math.ceil(value / 100) * 100
        elif (self.isBetween(1000, 10000, value)):
            return math.ceil(value / 1000) * 1000
        elif (self.isBetween(10000, 100000, value)):
            return math.ceil(value / 10000) * 10000

    def sameSign(self, num1, num2):
        return (num1 >= 0 and num2 >= 0) or (num1 < 0 and num2 < 0)

    def calculatePricePoints(self, spotPrice):
        spotPrice = getNearestStrike(
            spotPrice, self.underlying.stepValue)

        # start and end price points will be calculated based on this value, 10% from the value
        boundry = self.roundVal((spotPrice * 10) / 100)

        # step value will be calculated based on this value, 10 % from the value
        step = self.roundVal((boundry * 1) / 100)

        return {"boundry": boundry, "step": step}

    def calculatePositionsProfitLoss(self):
        self.priceList = []
        self.profitLossList = []

        if self.positions and len(self.positions) > 0:
            try:
                spotPrice = getNearestStrike(
                    self.positions[0].spotPrice, self.underlying.stepValue)

                pricePoints = self.calculatePricePoints(spotPrice)
                startPrice = spotPrice - pricePoints["boundry"]
                endPrice = spotPrice + pricePoints["boundry"]
                increment = pricePoints["step"]

                for price in range(startPrice, endPrice+increment, increment):
                    self.priceList.append(price)

                    plTotal = 0
                    for position in self.positions:
                        pl = self.positionProfitLossByPrice(position, price)
                        plTotal = plTotal+pl

                    self.profitLossList.append(plTotal)

            except Exception as e:
                print(e)

        return {"priceList": self.priceList, "profitLossList": self.profitLossList}

    def getMaxProfit(self):
        first = self.profitLossList[0]
        second = self.profitLossList[1]
        beforelast = self.profitLossList[-2]
        last = self.profitLossList[-1]

        if last > beforelast:
            return "Unlimited"
        else:
            if first > second:
                return "Unlimited"
            else:
                return max(self.profitLossList)

    def getMaxLoss(self):
        first = self.profitLossList[0]
        second = self.profitLossList[1]
        beforelast = self.profitLossList[-2]
        last = self.profitLossList[-1]

        if last < beforelast:
            return "Unlimited"
        else:
            if first < second:
                return "Unlimited"
            else:
                return min(self.profitLossList)

    def getRiskRewardRatio(self, profit, loss):
        ratio = "N/A"
        try:
            if type(profit) != 'int' or type(loss) != 'int':
                return ratio

            if profit > 0 and abs(loss) > 0:
                ratio = profit / abs(loss)
        except Exception as e:
            print(e)
        return ratio

    def calculateMaxProfitLoss(self):
        maxprofit = self.getMaxProfit()
        maxloss = self.getMaxLoss()
        riskRewardRatio = self.getRiskRewardRatio(maxprofit, maxloss)

        return {"maxprofit": maxprofit, "maxloss": maxloss, "riskRewardRatio": riskRewardRatio}

    def calculateBreakEven(self):
        strikePriceList = [0]
        for position in self.positions:
            strikePriceList.append(position.strikePrice)
        strikePriceList.append(1000000000)
        strikePriceList.sort()

        priceList = []
        profitLossList = []
        for price in strikePriceList:
            priceList.append(price)
            plTotal = 0
            for position in self.positions:
                pl = self.positionProfitLossByPrice(
                    position, price) * position.lotSize * position.noOfLots
                plTotal = plTotal + pl
            profitLossList.append(plTotal)

        length = len(profitLossList)
        isSameSign = False
        beakevenList = []
        for index in range(1, length, 1):
            breakeven = 0
            pl1 = profitLossList[index - 1]
            pl2 = profitLossList[index]
            isSameSign = self.sameSign(pl1, pl2)

            if not isSameSign:
                p1 = priceList[index - 1]
                p2 = priceList[index]
                breakeven = p1 + ((p2 - p1)*(0-pl1))/(pl2-pl1)
                beakevenList.append(breakeven)

        return {"beakevenList": beakevenList}

    def calculateDebitCredit(self):
        credit = 0
        debit = 0
        netCreditDebit = 0
        for position in self.positions:
            if (position.option == "CE" and position.transaction == "buy"):
                amount = position.premium * position.noOfLots * position.lotSize
                debit = debit + amount
            elif (position.option == "CE" and position.transaction == "sell"):
                amount = position.premium * position.noOfLots * position.lotSize
                credit = credit + amount
            elif (position.option == "PE" and position.transaction == "buy"):
                amount = position.premium * position.noOfLots * position.lotSize
                debit = debit + amount
            elif (position.option == "PE" and position.transaction == "sell"):
                amount = position.premium * position.noOfLots * position.lotSize
                credit = credit + amount

        netCreditDebit = credit - debit
        return {"credit": credit, "debit": debit, "netCreditDebit": netCreditDebit}
