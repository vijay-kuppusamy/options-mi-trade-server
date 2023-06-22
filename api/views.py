from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
import logging

from . import angelOneAuthViews as angelOne
from . import strategyViews
from . import tradeViews

logger = logging.getLogger("optionsmi")

@api_view(['GET', 'POST'])
def angelOneLogin(request):
    return angelOne.angelOnelogin(request)


@api_view(['GET'])
def angelOneLogout(request):
    response = {'message': 'logout success'}
    return Response(response)


@api_view(['GET'])
def authenticate(request):
    if request.user.is_authenticated:
        logger.info("Logged in user : ", request.user)
        return Response({'response': {"user": request.user.username}})
    else:
        logger.info("usre not logged in")
        return Response({"message": "User not logged in"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET', 'POST'])
def getAllStrategies(request):
    return strategyViews.getAllStrategies(request)


@api_view(['GET', 'POST'])
def getStrategy(request):
    return strategyViews.getStrategy(request)


@api_view(['GET', 'POST'])
def saveStrategy(request):
    return strategyViews.saveStrategy(request)


@api_view(['GET', 'POST'])
def deleteStrategy(request):
    return strategyViews.deleteStrategy(request)


@api_view(['GET', 'POST'])
def paperTrade(request):
    return tradeViews.paperTrade(request)
