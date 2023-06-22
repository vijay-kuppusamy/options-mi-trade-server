
from base.models import Strategy, AlgoOrder
from base.tasks import create_algoorder


def run():
    try:
        print("Start : Test Algo Order")
        strategy = Strategy.objects.get(pk=1)
        user = strategy.user
        settings = strategy.settings
        positions = strategy.positions

        order = AlgoOrder.objects.create(
            user=user, settings=settings, positions=positions)

        print(order.id)

        # create_algoorder.delay({"algoorderid": order.id})

        print("End : Test Algo Order")
    except Exception as e:
        print(e)
