from django.contrib import admin
from .models import Profile, TradingSession, Strategy
from .models import ScripMaster, ExpiryDate, StrikePrice
from .models import AlgoOrder, AlgoPosition, TradingPrice


admin.site.register(Profile)
admin.site.register(TradingSession)
admin.site.register(Strategy)
admin.site.register(ScripMaster)
admin.site.register(ExpiryDate)
admin.site.register(StrikePrice)
admin.site.register(AlgoOrder)
admin.site.register(AlgoPosition)
admin.site.register(TradingPrice)
