from django.contrib.auth.models import User
from base.models import TradingPrice, AlgoOrder, AlgoPosition
from datetime import datetime

def run():
    try:
        print("Test Run")

        try:
            user = User.objects.get(pk=1)
            # prices = list(TradingPrice.objects.filter(
            #     user=user).values("symbol", "symboltoken", "price"))
            # print(prices)

            # orders = AlgoOrder.objects.prefetch_related('algoposition_set').filter(user=user).values("id", "papertrade", "status", "user")
            # print(list(orders))

            today = datetime.now()
            print(today)
            
            algoOrders = []
            orders = list(AlgoOrder.objects.filter(user=user, created__date=today.date()).values(
                "id", "papertrade", "status", "user"))
            # print(orders)
            for order in orders:
                # print(order)
                # print(order['id'])
                positions = list(AlgoPosition.objects.filter(order_id=order['id']).values(
                    "symbol", "option", "quantity", "ordertype", "producttype", "transaction", "buyPrice", "status"))
                # print(positions)
                algoOrders.append({"order": order, "positions": positions})

            print(algoOrders)

        except Exception as e:
            print(e)

        print("Test End")
    except Exception as e:
        print(e)
