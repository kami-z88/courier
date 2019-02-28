"""DjangoBoilerplate URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
	https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
	1. Add an import:  from my_app import views
	2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
	1. Add an import:  from other_app.views import Home
	2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
	1. Import the include() function: from django.conf.urls import url, include
	2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url, include
from django.contrib.flatpages import views

from rest_framework import routers, serializers, viewsets

from account.views import signup, signin, signout, activate, profile, profile_edit, account_edit, profile_list
from courier.views import home_page, user_deposit, user_delivery, user_payments, user_tracking,\
	visitor_services, visitor_about, visitor_contact, visitor_portfolio, visitor_tracking,\
	dispatcher_archive, dispatcher_payments, dispatcher_tasks, dispatcher_users,\
	courier_delivered, courier_tasks,courier_tasks_smart_sort, courier_tasks_custom_sort, courier_tasks_should_pickup, \
	courier_tasks_pickedup, courier_target_task, test_page, submit_user_delivery,\
	delivery_item, set_delivery_courier,set_delivery_rejection_reason,check_db_for_dispatcher, \
	put_task_on_target, check_db_for_courier, withdraw_target_task, courier_tasks_rejected_pickup, \
	reject_package_pickup, undo_reject_package_pickup, do_undo_pickup, done_width_pickup, carry_back_package, \
	handover_package, visitor_tracking_ajax, user_address_book, \
	get_provinces, get_cities, add_update_user_address, get_user_address, delete_user_address, set_auto_dispatch_on, \
	set_auto_dispatch_off, unset_new_task_for_courier

from account.api import UserViewSet, ProfileViewSet, GroupViewSet
from courier.api import CourierViewSet, AddressViewSet, DepositViewSet, DispatcherViewSet,\
	OnlinePaymentViewSet, PackageTemplateViewSet, PackageViewSet, PaymentViewSet, DeliveryViewSet

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'profile', ProfileViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'courier', CourierViewSet)
router.register(r'address', AddressViewSet)
router.register(r'deposit', DepositViewSet)
router.register(r'dispatcher', DispatcherViewSet)
router.register(r'online-payment', OnlinePaymentViewSet)
router.register(r'package-template', PackageTemplateViewSet)
router.register(r'package', PackageViewSet)
router.register(r'payment', PaymentViewSet)
router.register(r'delivery', DeliveryViewSet)

urlpatterns = [
	# home
	url(r'^$', home_page, name="home"),
	url(r'^home/ajax/visitor-tracking', visitor_tracking_ajax),
	# admin
	url(r'^admin/', admin.site.urls, name='admin'),
	# User Accounts
	url(r'^signup/$', signup, name='signup'),
	url(r'^login/$', signin, name='signin'),
	url(r'^logout/$', signout, {'next_page': '/'}, name='signout'),
	url(r'^activate/(?P<activation_key>\w+)/$', activate, name='activate'),
	url(r'^activate/retry/(?P<activation_key>\w+)/$', activate, name='activate_retry'),
	url(r'^activate_success/$', activate, name='activate_success'),

	url(r'^profile/(?P<username>[-\w]+)$', profile, name="profile"),
	url(r'^profile/(?P<username>[-\w]+)/edit-account$', account_edit, name="account_edit"),
	url(r'^profile/(?P<username>[-\w]+)/edit-profile$', profile_edit, name="profile_edit"),
	# Restful API
	# url(r'^api-auth/', include('rest_framework.urls')),
	url(r'^api/', include(router.urls)),

	# User Pages
	url(r'^user/tracking', user_tracking, name="user_tracking"),
	url(r'^user/delivery$', user_delivery, name="user_delivery"),
	url(r'^user/address-book$', user_address_book, name="user_address_book"),
	url(r'^user/delivery-report/(?P<slug>[-\w]+)$', delivery_item, name="delivery_report"),
	url(r'^history/deposit$', user_deposit, name="user_deposit"),
	url(r'^history/payments', user_payments, name="user_payments"),
	url(r'^user/ajax/add-update-address', add_update_user_address),
	url(r'^user/ajax/user-delivery', submit_user_delivery),
	url(r'^user/ajax/get-provinces', get_provinces),
	url(r'^user/ajax/get-cities', get_cities),
	url(r'^user/ajax/get-user-address', get_user_address),
	url(r'^user/ajax/delete-user-address', delete_user_address),

	# Visitor pages
	url(r'^services$', visitor_services, name="visitor_services"),
	url(r'^about$', visitor_about, name="visitor_about"),
	url(r'^contact$', visitor_contact, name="visitor_contact"),
	url(r'^portfolio$', visitor_portfolio, name="visitor_portfolio"),
	url(r'^visitor/tracking', visitor_tracking, name="visitor_tracking"),

	# Dispatcher pages
	url(r'^dispatcher/tasks', dispatcher_tasks, name="dispatcher_tasks"),
	url(r'^dispatcher/archive', dispatcher_archive, name="dispatcher_archive"),
	url(r'^dispatcher/users', dispatcher_users, name="dispatcher_users"),
	url(r'^dispatcher/payments', dispatcher_payments, name="dispatcher_payments"),
	url(r'^dispatcher/ajax/set-courier', set_delivery_courier),
	url(r'^dispatcher/ajax/set-delivery-rejection-reason', set_delivery_rejection_reason),
	url(r'^dispatcher/ajax/check-db-for-dispatcher', check_db_for_dispatcher),
	url(r'^dispatcher/ajax/set-auto-dispatch-on', set_auto_dispatch_on),
	url(r'^dispatcher/ajax/set-auto-dispatch-off', set_auto_dispatch_off),

	# Courier pages
	url(r'^courier/tasks/smart-sort', courier_tasks_smart_sort, name="smart_sort"),
	url(r'^courier/tasks/custom-sort', courier_tasks_custom_sort, name="custom_sort"),
	url(r'^courier/tasks/should-pickup', courier_tasks_should_pickup, name="should_pickup"),
	url(r'^courier/tasks/pickedup', courier_tasks_pickedup, name="pickedup"),
	url(r'^courier/tasks/rejected-pickup', courier_tasks_rejected_pickup, name="rejected_pickup"),
	url(r'^courier/tasks/target-task',courier_target_task, name="target_task"),
	url(r'^courier/tasks', courier_tasks, name="courier_tasks"),
	url(r'^courier/delivered', courier_delivered, name="courier_delivered"),
	url(r'^courier/ajax/put-task-on-target', put_task_on_target, name="put_on_target"),
	url(r'^courier/ajax/check-db-for-courier', check_db_for_courier),
	url(r'^courier/ajax/unset-new-task-for-courier', unset_new_task_for_courier),
	url(r'^courier/ajax/withdraw-target-task', withdraw_target_task),
	url(r'^courier/ajax/reject-package-pickup', reject_package_pickup),
	url(r'^courier/ajax/undo-reject-package-pickup', undo_reject_package_pickup),
	url(r'^courier/ajax/do-undo-pickup', do_undo_pickup),
	url(r'^courier/ajax/done-width-pickup', done_width_pickup),
	url(r'^courier/ajax/carry-back-package', carry_back_package),
	url(r'^courier/ajax/handover-package', handover_package),


	url(r'^test-page', test_page, name="test_page"),


	# all the pages
	url(r'^(?P<slug>[-\w]+)$', views.flatpage),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)