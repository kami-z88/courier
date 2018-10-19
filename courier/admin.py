from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import AvailableTime, ServiceType, Dispatcher, Courier, Delivery, DepositPayment, Payment, Address, AddressBook, PackageTemplate, Package, OnlinePayment

class AvailableTimeInline(admin.TabularInline):
	model = ServiceType.available_time.through
	verbose_name = u"Available Time"
	verbose_name_plural = u"Available Time"


class ServiceTypeAdmin(admin.ModelAdmin):
	exclude = ("available_time",)
	inlines = (
		AvailableTimeInline,
	)


class AvailableTimeAdmin(admin.ModelAdmin):
	list_display = ['weekday','from_hour','to_hour']


class DispatcherAdmin(admin.ModelAdmin):
	list_display = ['user','avatar']


class CourierAdmin(admin.ModelAdmin):
	list_display = ['user','avatar']

class Addressline(admin.TabularInline):
	model = Address


class DeliveryAdmin(admin.ModelAdmin):
	list_display = ['tracking_id','status','cost','payment_type']


class DepositAdmin(admin.ModelAdmin):
	list_display = [field.name for field in DepositPayment._meta.get_fields()]


class PaymentAdmin(admin.ModelAdmin):
	list_display = [field.name for field in Payment._meta.get_fields()]


class AddressAdmin(admin.ModelAdmin):
	list_display = ['address1','address2','city','state','zip','phone']

class AddressBookAdmin(admin.ModelAdmin):
	pass

class PackageTemplateAdmin(admin.ModelAdmin):
	pass

class PackageAdmin(admin.ModelAdmin):
	pass


class OnlinePaymentAdmin(admin.ModelAdmin):
	list_display = ['user','value','meta']





admin.site.register(AvailableTime, AvailableTimeAdmin)
admin.site.register(ServiceType, ServiceTypeAdmin)
admin.site.register(Dispatcher, DispatcherAdmin)
admin.site.register(Courier, CourierAdmin)
admin.site.register(Delivery, DeliveryAdmin)
admin.site.register(DepositPayment, DepositAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(AddressBook, AddressBookAdmin)
admin.site.register(PackageTemplate, PackageTemplateAdmin)
admin.site.register(Package, PackageAdmin)
admin.site.register(OnlinePayment, OnlinePaymentAdmin)

