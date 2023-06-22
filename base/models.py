import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobileno = models.CharField(max_length=12, blank=True)
    exchanges = models.CharField(max_length=100, blank=True)
    products = models.CharField(max_length=100, blank=True)
    brokerid = models.CharField(max_length=100, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class TradingSession(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    apikey = models.CharField(max_length=100, blank=True)
    secretkey = models.CharField(max_length=100, blank=True)
    jwtToken = models.TextField(max_length=300, blank=True)
    refreshToken = models.TextField(max_length=300, blank=True)
    feedToken = models.TextField(max_length=300, blank=True)
    taskid = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=30, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(post_save, sender=User)
def create_user_trading_session(sender, instance, created, **kwargs):
    if created:
        TradingSession.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_trading_session(sender, instance, **kwargs):
    instance.tradingsession.save()


class Strategy(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=30, blank=True)
    type = models.CharField(max_length=10, blank=True)
    settings = models.TextField(blank=True)
    positions = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (
            "user",
            "name",
        )


class ScripMaster(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    token = models.CharField(max_length=30, blank=True)
    symbol = models.CharField(max_length=100, blank=True)
    name = models.CharField(max_length=30, blank=True)
    instrumenttype = models.CharField(max_length=30, blank=True)
    exch_seg = models.CharField(max_length=30, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class ExpiryDate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    symbol = models.CharField(max_length=100, blank=True)
    expirydate = models.DateField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class StrikePrice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    symbol = models.CharField(max_length=100, blank=True)
    expirydate = models.DateField(blank=True)
    price = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class AlgoOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    settings = models.TextField(blank=True)
    positions = models.TextField(blank=True)
    papertrade = models.BooleanField(default=False)
    status = models.CharField(max_length=30, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class AlgoPosition(models.Model):
    order = models.ForeignKey(AlgoOrder, on_delete=models.CASCADE)
    buyOrderId = models.CharField(max_length=100, blank=True)
    buyOrderStatus = models.CharField(max_length=100, blank=True)
    sellOrderId = models.CharField(max_length=100, blank=True)
    sellOrderStatus = models.CharField(max_length=100, blank=True)
    symbol = models.CharField(max_length=100, blank=True)
    symboltoken = models.CharField(max_length=30, blank=True)
    exch_seg = models.CharField(max_length=30, blank=True)
    option = models.CharField(max_length=30, blank=True)
    quantity = models.IntegerField(default=0)
    ordertype = models.CharField(max_length=30, blank=True)
    producttype = models.CharField(max_length=30, blank=True)
    transaction = models.CharField(max_length=30, blank=True)
    buyPrice = models.FloatField(default=0)
    sellPrice = models.FloatField(default=0)
    target = models.BooleanField(default=False)
    targetType = models.CharField(max_length=30, blank=True)
    targetValue = models.IntegerField(default=0)
    stoploss = models.BooleanField(default=False)
    stoplossType = models.CharField(max_length=30, blank=True)
    stoplossValue = models.IntegerField(default=0)
    trailSL = models.BooleanField(default=False)
    trailSLType = models.CharField(max_length=30, blank=True)
    trailSLValue = models.IntegerField(default=0)
    pl = models.FloatField(default=0)
    plAmt = models.FloatField(default=0)
    plPct = models.FloatField(default=0)
    trailPrice = models.FloatField(default=0)
    status = models.CharField(max_length=30, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class SubscribeSymbol(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    symboltoken = models.CharField(max_length=30, blank=True)
    exch_seg = models.CharField(max_length=30, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class TradingPrice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=100, blank=True)
    symboltoken = models.CharField(max_length=30, blank=True)
    exch_seg = models.CharField(max_length=30, blank=True)
    price = models.FloatField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (
            "user",
            "symbol",
        )


class Underlying(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    symbol = models.CharField(unique=True, max_length=100, blank=True)
    underlying = models.CharField(max_length=100, blank=True)
    underlyingType = models.CharField(max_length=100, blank=True)
    lotSize = models.IntegerField(default=0)
    qtyFrezze = models.IntegerField(default=0)
    stepValue = models.FloatField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
