from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import AvailableTime, ServiceType, Dispatcher, Courier, Delivery,\
	DepositPayment, Payment, Address, PackageTemplate, Package,\
	OnlinePayment, Country, Province, City, Comment


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
	list_display = ['user','photo']


class CourierAdmin(admin.ModelAdmin):
	list_display = ['user']


class Addressline(admin.TabularInline):
	model = Address


class DeliveryAdmin(admin.ModelAdmin):
	list_display = ['status','cost','payment_type']


class DepositAdmin(admin.ModelAdmin):
	list_display = [field.name for field in DepositPayment._meta.get_fields()]


class PaymentAdmin(admin.ModelAdmin):
	list_display = [field.name for field in Payment._meta.get_fields()]


class AddressAdmin(admin.ModelAdmin):
	list_display = ['id', 'address1', 'address2', 'city', 'zip', 'phone']


class CommentAdmin(admin.ModelAdmin):
	list_display = [f.name for f in Comment._meta.fields]


class PackageTemplateAdmin(admin.ModelAdmin):
	pass


class PackageAdmin(admin.ModelAdmin):
	pass


class OnlinePaymentAdmin(admin.ModelAdmin):
	list_display = ['user','value','meta']


class CountryAdmin(admin.ModelAdmin):
	list_display = ['name']


class ProvinceAdmin(admin.ModelAdmin):
	list_display = ['name', 'country']


class CityAdmin(admin.ModelAdmin):
	list_display = ['name', 'province']


admin.site.register(AvailableTime, AvailableTimeAdmin)
admin.site.register(ServiceType, ServiceTypeAdmin)
admin.site.register(Dispatcher, DispatcherAdmin)
admin.site.register(Courier, CourierAdmin)
admin.site.register(Delivery, DeliveryAdmin)
admin.site.register(DepositPayment, DepositAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(PackageTemplate, PackageTemplateAdmin)
admin.site.register(Package, PackageAdmin)
admin.site.register(OnlinePayment, OnlinePaymentAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Province, ProvinceAdmin)
admin.site.register(City, CityAdmin)

