# import time
# def run():
#     try:
#         print("Test Run")
#         print("Test End")
#     except Exception as e:
#         print(e)

# from channels import Group
# from django.db.models import signals
# from django.dispatch import receiver


# @receiver(signals.post_save, sender=Factory)
# def notify_group(sender, instance, **kwargs):
#     if kwargs['created']:
#         group_name = 'your group'
#         Group(group_name).send({'text': 'message or object'})


from django.contrib.auth.models import User
from base.models import SubscribeSymbol, TradingPrice, ExpiryDate
import logging
from datetime import datetime

def run():
    try:
        print("Test Run")
        logger = logging.getLogger(__name__)

        try:

            today = datetime.now()
            print(today.date())

            symbol = "NIFTY"
            dates = list(ExpiryDate.objects.filter(symbol=symbol, created__date = today.date()).order_by('expirydate').values())
            print(dates)

        except Exception as e:
            print(e)

        print("Test End")
    except Exception as e:
        print(e)
