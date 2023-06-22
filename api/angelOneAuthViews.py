from django.conf import settings
from django.middleware import csrf
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from celery.result import AsyncResult

from smartapi import SmartConnect
from base.tasks import create_tradingsession


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
# End get_tokens_for_user

def angelOnelogin(request):
    if request.method == 'POST':
        data = request.data
        print(data)
        response = Response()
        if data:
            try:
                username = data['clientId']
                password = data['password']
                totp = data['totp']

                # TODO
                api_key = "fOQCAV0P"

                connection = SmartConnect(api_key=api_key)

                data = connection.generateSession(username, password, totp)

                if data['data']['jwtToken'] is None:
                    return Response({"message": "Invalid username or password"}, status=status.HTTP_404_NOT_FOUND)

                pw = "optionmi4"+username
                user = authenticate(username=username, password=pw)
                if user is None:
                    print("creating user")
                    # pass - optionmi4+<username>
                    # Just a password - no use for it
                    # System will use broker auth
                    user = User.objects.create_user(username, '', pw)

                # If the session is alive, kill the task
                taskid = user.tradingsession.taskid
                AsyncResult(taskid).revoke(terminate=True)

                # Create a trading session, this will start a socket connection with broker server
                result = create_tradingsession.delay({"id": user.id})

                # Get details from angelone login response
                user.tradingsession.jwtToken = connection.access_token
                user.tradingsession.refreshToken = connection.refresh_token
                user.tradingsession.feedToken = connection.feed_token
                user.tradingsession.taskid = result.id
                user.save()

                data = get_tokens_for_user(user)
                response.set_cookie(
                    key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                    value=data["access"],
                    expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
                    secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                    httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                    samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
                )
                csrf.get_token(request)
                response.data = {'response': {
                    "user": user.username, "data": data}}
                return response
            except Exception as e:
                print(e)
                return Response({"message": "Invalid username or password"}, status=status.HTTP_404_NOT_FOUND)

    else:
        if request.user.is_authenticated:
            print("Logged in user : ", request.user)
            return Response({'response': 'user logged in'})
        else:
            return Response({'response': 'user not logged in'})
# End angelOnelogin