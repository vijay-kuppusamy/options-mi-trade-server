import time

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from base.models import TradingPrice, AlgoOrder, AlgoPosition
from datetime import datetime

@database_sync_to_async
def get_prices(user):
    prices = list(TradingPrice.objects.filter(
        user=user).values("symbol", "price"))
    return prices

@database_sync_to_async
def get_orders(user):
    today = datetime.now()
    algoOrders = []
    orders = list(AlgoOrder.objects.filter(user=user, created__date=today.date()).values("id", "papertrade", "status", "user"))
    for order in orders:
        positions = list(AlgoPosition.objects.filter(order_id=order['id']).values("symbol", "option", "quantity", "ordertype", "producttype", "transaction", "buyPrice", "status"))
        algoOrders.append({"order":order, "positions":positions})

    return algoOrders

class WsConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.isConnected = False

    async def connect(self):
        await self.accept()
        self.isConnected = True
        print("Connected")
        user = self.scope['user']
        print("logged in user {}".format(user))
        await self.send(text_data='{"message": "welcome" }')
        while self.isConnected:
            # Sending live price
            prices = await get_prices(user)
            msg_price = {"type": "price_update", "data": prices}
            await self.send(text_data=str(msg_price))
            orders = await get_orders(user)
            msg_order = {"type": "order_update", "data": orders}
            await self.send(text_data=str(msg_order))
            time.sleep(3)

    async def receive(self, *, text_data):
        print("Received {}".format(text_data))

    async def disconnect(self, message):
        self.isConnected = False
        print("Disconnected")
