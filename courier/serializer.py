from django.conf.urls import url, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from courier.models import Dispatcher, Courier, Delivery, DepositPayment, Payment, Address, PackageTemplate, Package, OnlinePayment
from rest_framework import serializers


class CourierSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Courier
        fields = "__all__"


class DispatcherSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Dispatcher
        fields = "__all__"


class CourierSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Courier
        fields = "__all__"


class DeliverySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Delivery
        fields = "__all__"


class DepositSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DepositPayment
        fields = "__all__"


class PaymentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"


class AddressSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"


class PackageTemplateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PackageTemplate
        fields = "__all__"


class PackageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Package
        fields = "__all__"


class OnlinePaymentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OnlinePayment
        fields = "__all__"
