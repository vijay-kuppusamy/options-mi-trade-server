from urllib.parse import parse_qs
from django.conf import settings
from django.contrib.auth import get_user_model
from jwt import decode as jwt_decode
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.authentication import CSRFCheck
from rest_framework import exceptions
from asgiref.sync import sync_to_async


def dummy_get_response(request):  # pragma: no cover
    return None


def enforce_csrf(request):
    check = CSRFCheck(dummy_get_response)
    check.process_request(request)
    reason = check.process_view(request, None, (), {})
    if reason:
        raise exceptions.PermissionDenied('CSRF Failed: %s' % reason)


class CustomAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)

        if header is None:
            raw_token = request.COOKIES.get(
                settings.SIMPLE_JWT['AUTH_COOKIE']) or None
        else:
            raw_token = self.get_raw_token(header)
            
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        enforce_csrf(request)
        return self.get_user(validated_token), validated_token


@sync_to_async
def get_user(user_id):
    return get_user_model().objects.get(id=user_id)


class ChannelJwtAuthMiddleWare:

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # Get the token
        query_string = scope["query_string"]
        query_params = query_string.decode()
        query_dict = parse_qs(query_params)
        token = query_dict["token"][0]
        print(token)

        # Try to authenticate the user
        try:
            # This will automatically validate the token and raise an error if token is invalid
            UntypedToken(token)
        except (InvalidToken, TokenError) as e:
            # Token is invalid
            print(e)
            return None
        else:
            #  Then token is valid, decode it
            decoded_data = jwt_decode(
                token, settings.SECRET_KEY, algorithms=["HS256"])
            print(decoded_data)
            # Will return a dictionary like -
            # {
            #     "token_type": "access",
            #     "exp": 1568770772,
            #     "jti": "5c15e80d65b04c20ad34d77b6703251b",
            #     "user_id": 6
            # }
            # Get the user using ID
            user = await get_user(decoded_data["user_id"])

            scope["user"] = user

        # Return the inner application directly and let it run everything else
        return await self.app(scope, receive, send)
