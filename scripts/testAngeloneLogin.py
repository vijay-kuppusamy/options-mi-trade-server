from django.contrib.auth.models import User
from smartapi import SmartConnect


def run():
    try:
        print("Test Angelone Login")
        # App Name - options-mi-trade
        # API Key - fOQCAV0P
        # Secret Key - 81f3f61b-1f51-401d-9e30-353c9ab01474
        user = User.objects.get(pk=2)
        api_key = user.tradingsession.apikey
        print(api_key)

        connection = SmartConnect(api_key=api_key)
        data = connection.generateSession(
            "V515922", "1578", "280540")

        print(data)
        print(connection.access_token)
        print(connection.refresh_token)
        print(connection.feed_token)

        user.tradingsession.jwtToken = connection.access_token
        user.tradingsession.refreshToken = connection.refresh_token
        user.tradingsession.feedToken = connection.feed_token
        user.save()

    except Exception as e:
        print(e)
