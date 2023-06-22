import json
from django.forms.models import model_to_dict
from django.middleware import csrf
from rest_framework.response import Response
from rest_framework import status

from base.models import Strategy
from base.payoff import Payoff
from base.business import getStrategySettings


def builtinStrategy(request):
    if request.method == 'POST':
        response = {}
        data = request.data
        print(data)
        if data:
            try:
                print(data["name"])
                settings = getStrategySettings(data["name"])
                response = {'response': settings}
            except Exception as e:
                response = {'error': str(e)}

        return Response(response)
    else:
        response = {'message': 'Strategy Details Get'}
        return Response(response)


def builtinStrategyPayoff(request):
    if request.method == 'POST':
        response = {}
        data = request.data
        print(data)
        # if data:
        # try:
        #     settings = getStrategySettings("short_strangle")
        #     underlyingSymbol = settings['underlying']
        #     positions = loadPositions(settings)
        #     underlying = Underlying(underlyingSymbol, 50, 50)

        #     payoff = Payoff(positions, underlying)
        #     payoffValues = dict()
        #     pl = payoff.calculatePositionsProfitLoss()
        #     maxPl = payoff.calculateMaxProfitLoss()
        #     breakEven = payoff.calculateBreakEven()
        #     netCreditDebit = payoff.calculateDebitCredit()

        #     payoffValues.update(pl)
        #     payoffValues.update(maxPl)
        #     payoffValues.update(breakEven)
        #     payoffValues.update(netCreditDebit)
        #     response = {'response': payoffValues}
        # except Exception as e:
        #     response = {'error': str(e)}

        return Response(response)
    else:
        response = {'message': 'Strategy Details Get'}
        return Response(response)


def getStrategy(request):
    if request.method == 'POST':
        try:
            if request.user.is_authenticated:
                data = request.data
                id = data["id"]
                strategy = Strategy.objects.get(pk=id)
                return Response({'response': model_to_dict(strategy)})
            else:
                return Response({"message": "User not logged in"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'message': str(e)})

    else:
        return Response({'message': 'Get Strategy'})
# End getStrategy


def getAllStrategies(request):
    if request.method == 'POST':
        response = {'message': 'Strategy Details Post'}
        return Response(response)
    else:
        try:
            if request.user.is_authenticated:
                strategyNames = list(Strategy.objects.filter(
                    user=request.user).values("id", "name"))
                return Response({'response': strategyNames})
            else:
                return Response({"message": "User not logged in"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'message': str(e)})
# End getAllStrategies


def saveStrategy(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            data = request.data
            print(data)
            requestStrategy = data["strategy"]
            name = requestStrategy["name"]

            settings = data["settings"]
            positions = data["positions"]

            id = None
            if 'id' in requestStrategy:
                id = requestStrategy["id"]

            notes = None
            if 'notes' in requestStrategy:
                notes = requestStrategy["notes"]

            if id is not None:
                id = requestStrategy["id"]
                strategy = Strategy.objects.get(pk=id)
                strategy.settings = settings
                strategy.positions = positions
                strategy.save()
                return Response({'response': 'Strategy Saved'})
            else:
                # checking if the name already exists
                exist = Strategy.objects.filter(
                    name=name, user=request.user).first()
                if not exist:
                    strategy = Strategy.objects.create(
                        user=request.user, name=name, type="custom", settings=settings, positions=positions, notes=notes)
                    return Response({'response': 'Strategy Saved'})
                else:
                    return Response({"message": "Strategy name exists"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "User not logged in"}, status=status.HTTP_401_UNAUTHORIZED)

    else:
        return Response({'message': 'Strategy Save Get'})
# End saveStrategy


def deleteStrategy(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            try:
                data = request.data
                id = data["id"]
                strategy = Strategy.objects.get(pk=int(id))
                strategy.delete()
                return Response({'response': 'Strategy Deleted'})
            except Exception as e:
                return Response({"message": "Error while deleting Strategy"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "User not logged in"}, status=status.HTTP_401_UNAUTHORIZED)

    else:
        return Response({'message': 'Strategy Save Get'})
# End deleteStrategy
