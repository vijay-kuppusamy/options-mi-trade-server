from rest_framework.response import Response
from rest_framework import status
from base.models import AlgoOrder
from base.tasks import create_papertrade


def paperTrade(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            try:
                data = request.data
                user = request.user
                print(data)
                print(user)
                settings = data["settings"]
                positions = data["positions"]

                order = AlgoOrder.objects.create(
                    user=user, settings=settings, positions=positions, papertrade=True, status="Pending")
                print(order.id)
                result = create_papertrade.delay({"algoorderid": order.id})
                

                return Response({'response': 'Order Created'})
            except Exception as e:
                return Response({"message": "Error while executing paper trade"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "User not logged in"}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({'message': 'paper trade'})
# End paperTrade
