from celery import shared_task
from datetime import datetime
from base.utils import getDateTime
import logging
import time
import pytz

import base.settings as settings
from base.models import AlgoOrder
from broker.paperTrade import papertrade
from broker.tradingSession import tradingsession
from base.models import TradingPrice

logger = logging.getLogger("tasks")

@shared_task(name="create_tradingsession")
def create_tradingsession(request):
    print(request)
    id = request["id"]
    return tradingsession(id)


@shared_task(name="create_papertrade")
def create_papertrade(request):
    print(request)
    algoorderid = request["algoorderid"]
    return papertrade(algoorderid)


@shared_task(name="create_algoorder")
def create_algoorder(request):
    print(request)
    algoorderid = request["algoorderid"]
    algoOrder = AlgoOrder.objects.get(pk=algoorderid)
    return {"status": "success"}


@shared_task(name="sample_task")
def sample_task(request):
    logger.info(request)
    id = request["id"]

    try:
        end_time = getDateTime(request["time"])

        marketOpen = True
        while marketOpen:
            now = datetime.now(pytz.timezone("Asia/Kolkata"))
            logger.info("id : {}".format(id))
            logger.info("market open: {}".format(now))

            if now.time() >= end_time.time():
                marketOpen = False
            time.sleep(1)
        # End while 
        
    except Exception as e:
        logger.error(e. e.__traceback__)

    return {"status": "success"}