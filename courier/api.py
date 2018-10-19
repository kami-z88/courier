from rest_framework import viewsets
from .models import Dispatcher, Courier, Delivery, DepositPayment, Payment, Address, PackageTemplate, Package, OnlinePayment
from .serializer import DispatcherSerializer, CourierSerializer, DeliverySerializer, DepositSerializer, PaymentSerializer, AddressSerializer, PackageTemplateSerializer, PackageSerializer, OnlinePaymentSerializer


class DispatcherViewSet(viewsets.ModelViewSet):
	queryset = Dispatcher.objects.all()
	serializer_class = DispatcherSerializer


class CourierViewSet(viewsets.ModelViewSet):
	queryset = Courier.objects.all()
	serializer_class = CourierSerializer


class DeliveryViewSet(viewsets.ModelViewSet):
	queryset = Delivery.objects.all()
	serializer_class = DeliverySerializer


class DepositViewSet(viewsets.ModelViewSet):
	queryset = DepositPayment.objects.all()
	serializer_class = DepositSerializer


class PaymentViewSet(viewsets.ModelViewSet):
	queryset = Payment.objects.all()
	serializer_class = PaymentSerializer


class AddressViewSet(viewsets.ModelViewSet):
	queryset = Address.objects.all()
	serializer_class = AddressSerializer


class PackageTemplateViewSet(viewsets.ModelViewSet):
	queryset = PackageTemplate.objects.all()
	serializer_class = PackageTemplateSerializer


class PackageViewSet(viewsets.ModelViewSet):
	queryset = Package.objects.all()
	serializer_class = PackageSerializer


class OnlinePaymentViewSet(viewsets.ModelViewSet):
	queryset = OnlinePayment.objects.all()
	serializer_class = OnlinePaymentSerializer
