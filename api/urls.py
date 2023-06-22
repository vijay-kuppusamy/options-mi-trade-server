from django.urls import path
from . import views

urlpatterns = [
    path('auth/angelone/login', views.angelOneLogin),
    path('auth/angelone/logout', views.angelOneLogout),
    path('auth/authenticate', views.authenticate),
    path('strategy/get', views.getStrategy),
    path('strategy/all', views.getAllStrategies),
    path('strategy/save', views.saveStrategy),
    path('strategy/delete', views.deleteStrategy),
    path('strategy/papertrade', views.paperTrade),
]
