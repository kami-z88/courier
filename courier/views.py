from django.shortcuts import render, redirect
from courier.models import Dispatcher, Courier, Address, ServiceType, PackageTemplate,\
	Comment, Country, Province, City, ControlPanel
from courier.models import Delivery, Package
from django.contrib.auth.models import User
from account.models import Profile
from datetime import datetime, timedelta, time
import json
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q
from django.db import IntegrityError


cp = ControlPanel.load()


def home_page(request):
	context = {}
	if request.user.is_authenticated:
		if Courier.objects.filter(user=request.user).exists():
			return courier_home(request)
		elif Dispatcher.objects.filter(user=request.user).exists():
			return dispatcher_home(request)
		else:
			return render(request, "user-home.html", {'profile': Profile.objects.get(user=request.user)})
	else:
		from account.forms import SinginForm
		form = SinginForm()
		context = {
			'form': form
		}
		return render(request, "visitor-home.html", context)


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# $$$$$  Visitor  section $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def visitor_services(request):
	services = ServiceType.objects.all()
	b = services.count();
	context = {
		'services': services
	}

	return render(request, "visitor-services.html", context)


def visitor_about(request):
	context = {
		'visitor': 'test'
	}
	return render(request, "visitor-about.html", context)


def visitor_contact(request):
	context = {
		'visitor': 'test'
	}
	return render(request, "visitor-contact.html", context)


def visitor_portfolio(request):
	context = {
		'visitor': 'test'
	}
	return render(request, "visitor-portfolio.html", context)


def visitor_tracking(request):
	from .forms import TrackItemForm
	if request.method == 'POST':
		form = TrackItemForm(request.POST)
		if form.is_valid():
			context = {'form': form}
			tracking_code = form.cleaned_data['tracking_code']
			try:
				package = Package.objects.get(tracking_id=tracking_code)
				context['package'] = package
			except Package.DoesNotExist:
				context['error'] = 'Code is not valid!'
			return render(request, "visitor-tracking.html", context)
	else:
		form = TrackItemForm()

	context = {
		'form': form
	}
	return render(request, "visitor-tracking.html", context)


def visitor_tracking_ajax(request):
		code = request.GET.get('code', None)
		try:
			package = Package.objects.get(tracking_id=code.strip())
			if package.handover_time:
				deliver_time = "{0} {1}".format(package.handover_time.date(), package.handover_time.time().replace(second=0, microsecond=0))
			else:
				deliver_time = ""
			data = {
				'status': package.get_status_display(),
				'sender': package.delivery.get_user_proper_name(),
				'signer': package.signer_name,
				'deliver_time': deliver_time
			}
		except Package.DoesNotExist:
			data = {
				'error': 'Code is not valid!',
				'status': '',
				'sender': '',
				'signer': '',
				'deliver_time': ''
			}
		data = json.dumps(data)
		return HttpResponse(data, content_type='application/json')


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# $$$$$  User  section $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def user_tracking(request):
	deliveries = Delivery.objects.filter(user=request.user).order_by('-id')
	context = {
		'deliveries': deliveries,
		'x': request.user.role,
	}
	return render(request, "user-tracking.html", context)


def user_delivery(request):
	service_types = ServiceType.objects.all()
	package_templates = PackageTemplate.objects.all()
	addresses = Address.objects.filter(user=request.user, archived=False)
	countries = Country.objects.all()
	if countries.count() == 1:
		provinces = Province.objects.all()
		if provinces.count() == 1:
			cities = City.objects.all()
		else:
			cities = ""
	else:
		provinces = ""
		cities = ""

	context = {
		"addresses": addresses,
		'service_types': service_types,
		'package_templates': package_templates,
		'countries': countries,
		'provinces': provinces,
		'cities': cities,
		'zone_division_name': zone_division_name()
	}
	return render(request, "user-delivery.html", context)


def get_provinces(request):
	country_id = request.GET.get('country_id', None)
	country = Country.objects.get(id=country_id)
	provinces = Province.objects.filter(country=country)
	data = {}
	for province in provinces:
		data[province.id] = province.name.capitalize()
	if len(data) > 1:
		data[0] = "Select province ..."
	data = json.dumps(data, sort_keys=True)
	return HttpResponse(data, content_type='application/json')


def get_cities(request):
	province_id = request.GET.get('province_id', None)
	province = Province.objects.get(id=province_id)
	cities = City.objects.filter(province=province)
	data = {}
	for city in cities:
		data[city.id] = city.name.capitalize()
	if len(data) > 1:
		data[0] = "Select city ..."
	data = json.dumps(data, sort_keys=True)
	return HttpResponse(data, content_type='application/json')


def user_address_book(request):
	addresses = Address.objects.filter(user=request.user, archived=False)
	countries = Country.objects.all()
	if countries.count() == 1:
		provinces = Province.objects.all()
		if provinces.count() == 1:
			cities = City.objects.all()
		else:
			cities = ""
	else:
		provinces = ""
		cities = ""
	context = {
		"addresses": addresses,
		"countries": countries,
		"provinces": provinces,
		"cities": cities,
		'zone_division_name': zone_division_name()
	}
	return render(request, "user-address-book.html", context)


def add_update_user_address(request):
	address_data_str = request.GET.get('address_data', None)
	address_data_dict = json.loads(address_data_str)
	data = {}
	if address_data_dict['action'] == 'add':
		result = add_address(address_data_dict, request.user)
		data = {
			'address_id': result['address'].id,
			'error_type': result['error-type'],
			'error': result['error-message']
		}
	elif address_data_dict['action'] == 'update':
		result = update_address(address_data_dict, request.user)
		data = {
			'address_id': result['address'].id,
			'error_type': result['error-type'],
			'error': result['error-message']
		}
	data = json.dumps(data)
	return HttpResponse(data, content_type='application/json')


def get_user_address(request):
	data = {}
	address_id = request.GET.get('address_id', None);
	try:
		address = Address.objects.get(id=address_id, user=request.user)
		data = get_country_province_city_list(address.city.id)
		if address.title:
			data['title'] = address.title.capitalize()
		else:
			data['title'] = ""
		data['address1'] = address.address1
		data['address2'] = address.address2
		data['zip'] = address.zip
		data['phone'] = address.phone
		data['fax'] = address.fax
		data['email'] = address.email
		data['result'] = "success"
	except Address.DoesNotExist:
		data['result'] = "failed"
	data = json.dumps(data, sort_keys=True)
	return HttpResponse(data, content_type='application/json')


def delete_user_address(request):
	address_id = request.GET.get('address_id', None)
	result = delete_address(address_id, request.user)
	data = {}
	if result:
		data['result'] = "success"
	else:
		data['result'] = "failed"
	data = json.dumps(data)
	return HttpResponse(data, content_type='application/json')


def user_deposit(request):
	context = {
		'users': 'test',
	}
	return render(request, "user-deposit.html", context)


def user_payments(request):
	context = {
		'users': 'test',
	}
	return render(request, "user-payments.html", context)


def submit_user_delivery(request):
	from django.urls import reverse
	delivery_str = request.GET.get('delivery', None)
	delivery_data = json.loads(delivery_str)
	delivery = Delivery()
	delivery.user = request.user
	delivery.set_status_by_action("request_delivery", request.user.role)
	delivery.from_address = add_address(delivery_data["source_address"], request.user,'pa')['address']
	delivery.payment_type = "os"
	delivery.service_type = ServiceType.objects.get(pk=delivery_data["service_type"])
	delivery.save()
	for package_index in delivery_data["packages"]:
		package_data = delivery_data["packages"][package_index]
		package = Package()
		package.to_address = add_address(package_data, request.user, 'da')['address']
		package.template = PackageTemplate.objects.get(pk=package_data["template_id"])
		package.signature = package_data["signature"]
		package.tracking_code_sharing_sms = package_data["share_tracking_sms"]
		package.tracking_code_sharing_email = package_data["share_tracking_email"]
		package.description = package_data["description"]
		package.delivery = delivery
		package.save()
	if cp.auto_dispatch:  # If auto dispatch is on sets the delivery courier to intended courier
		delivery.courier = Courier.objects.get(id=cp.auto_dispatch_courier.id)
		cp.set_new_task_for_courier(cp.auto_dispatch_courier.id)
		delivery.set_status_by_action("auto_dispatch", 'auto_dispatch')
		delivery.save()
	result = {"status": "success", "redirect": request.build_absolute_uri(reverse('user_tracking'))}
	return HttpResponse(json.dumps(result), content_type='application/json')


def delivery_item(request, slug):
	delivery = Delivery.objects.get(id=slug)
	packages = Package.objects.filter(delivery=delivery)
	context = {
		"delivery": delivery,
		"packages": packages
	}
	return render(request, "user-delivery-details.html", context)


def cancel_delivery_request(request):
	delivery_id = request.GET.get("delivery_id", None)
	delivery = Delivery.objects.get(id=delivery_id, user=request.user)
	if delivery.status == "wd":
		delivery.set_status_by_action("cancel_before_dispatch", request.user.role)
	elif delivery.status == "wp":
		delivery.set_status_by_action("cancel_before_pickup", request.user.role)
	delivery.save()
	updated_delivery = Delivery.objects.get(id=delivery_id)
	data = {'result': ''}
	if updated_delivery.status == 'cbd' or updated_delivery.status == 'cbp':
		data['result'] = 'success'
	data = json.dumps(data)
	return HttpResponse(data, content_type='application/json')


def cancel_pickup_handover(request):
	package_id = request.GET.get("package_id", None)
	action = request.GET.get("action", None)
	package = Package.objects.get(id=package_id)
	if package.check_user(request.user) and package.is_mutable(request.user.role):
		package.set_status_by_action(action)
		package.save()
	data = {}
	if not package.is_mutable(request.user.role):
		data["result"] = "success"
	else:
		data["result"] = "failure"
	data = json.dumps(data)
	return HttpResponse(data, content_type='application/json')

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# $$$$$  Dispatcher  section $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def dispatcher_home(request):
	import itertools

	today = datetime.now().date()
	tomorrow = today + timedelta(1)
	today_start = datetime.combine(today, time())
	today_end = datetime.combine(tomorrow, time())

	# 24 hour chart data
	deliveries = Delivery.objects.filter(request_time_created__gte=today)
	grouped = itertools.groupby(deliveries, lambda item: item.request_time_created.strftime("%H"))
	deliveries_per_hour = {int(day): len(list(items_this_day)) for day, items_this_day in grouped}
	delivery_hours = dict((lambda x: ( datetime.strptime(str(x), '%H').strftime('%I %p') ,deliveries_per_hour[x]) if x in deliveries_per_hour else ( datetime.strptime(str(x), '%H').strftime('%I %p') ,0))(key) for key in range(0,24))
	request_chart_data = json.dumps(delivery_hours)

	deliveries_count = Delivery.objects.all().exclude(Q(status='rd',request_time_created__lte=today) | Q(status='rp',request_time_created__lte=today) | Q(status='d',request_time_created__lte=today)).count()
	deliveries_not_reviewed = Delivery.objects.filter(status='wd').count()
	waiting_for_courier = Delivery.objects.filter(request_time_created__gte=today,status='wc').count()
	on_road_to_pick = Delivery.objects.filter(status='ap').count()
	on_road_to_deliver = Delivery.objects.filter(status='pc').count()
	delivered_count = Delivery.objects.filter(request_time_created__gte=today, status='d').count()
	context = {
		'deliveries_count': deliveries_count,
		'deliveries_not_reviewed' : deliveries_not_reviewed,
		'waiting_for_courier': waiting_for_courier,
		'on_road_to_pick': on_road_to_pick,
		'on_road_to_deliver': on_road_to_deliver,
		'total_on_the_way': on_road_to_pick + on_road_to_deliver,
		'delivered_count': delivered_count,
		'request_chart_data': request_chart_data,
	}
	return render(request, "dispatcher-home.html", context)


def dispatcher_tasks(request):
	today = datetime.now().date()
	yesterday = today - timedelta(days=1)
	couriers = Courier.objects.all()
	deliveries_to_handle = Delivery.objects.filter(status='wd')
	reviewed_deliveries = Delivery.objects.filter(request_time_created__gte=yesterday).exclude(status='wd')
	couriers_info = {}
	for courier in couriers:
		user = User.objects.get(user=courier.user.id)
		user_name = user.username
		user_img_path = "/files/{}".format(Profile.objects.get(user=user).photo)
		couriers_info[courier.id] = {'userName':user_name, 'userImgPath':user_img_path}
	if cp.auto_dispatch:
		auto_dispatch_courier_id = cp.auto_dispatch_courier.id
	else:
		auto_dispatch_courier_id = ""
	context = {
		'couriers': couriers_info,
		'deliveries_to_handle': deliveries_to_handle,
		'reviewed_deliveries': reviewed_deliveries,
		'auto_dispatch': cp.auto_dispatch,
		'auto_dispatch_courier_id': auto_dispatch_courier_id
	}
	return render(request, "dispatcher-tasks.html", context)


def dispatcher_archive(request):
	context = {
		'x': request.user.role
	}
	return render(request, "dispatcher-archive.html", context)


def dispatcher_users(request):
	context = {
		'dispatcher': 'test'
	}
	return render(request, "dispatcher-users.html", context)


def dispatcher_payments(request):
	context = {
		'dispatcher': 'test'
	}
	return render(request, "dispatcher-payments.html", context)


def check_db_for_dispatcher(request):
	last_delivery_id = Delivery.objects.latest('id').id
	data = {
		'last_delivery_id': last_delivery_id,
	}
	data = json.dumps(data)
	return HttpResponse(data, content_type='application/json')


def set_delivery_courier(request):
	delivery_id = request.GET.get('delivery_id', None)
	courier_id = request.GET.get('courier_id', None)
	delivery = Delivery.objects.get(id=delivery_id)
	courier = Courier.objects.get(id=courier_id)
	dispatcher = Dispatcher.objects.get(user=request.user)
	delivery.courier = courier
	delivery.set_status_by_action("dispatch", request.user.role)
	delivery.dispatcher = dispatcher
	delivery.save()
	updated_delivery = Delivery.objects.get(id=delivery_id)
	if (str(updated_delivery.courier.id) == courier_id) and (updated_delivery.status == 'wc') :
		cp.set_new_task_for_courier(courier_id)
		data = {
			'result': 'success'
		}
	else:
		data = {
			'result': 'failed'
		}
	data = json.dumps(data)
	return HttpResponse(data, content_type='application/json')


def set_delivery_rejection_reason(request):
	delivery_id = request.GET.get('delivery_id', None)
	comment_text = request.GET.get('reason', None)
	delivery = Delivery.objects.get(id=delivery_id)
	dispatcher = Dispatcher.objects.get(user=request.user)
	delivery.set_status_by_action("reject_delivery", request.user.role)
	delivery.dispatcher = dispatcher
	delivery.save()
	new_comment = Comment()
	new_comment.set_actor(request)
	new_comment.user = request.user
	new_comment.reason = 'dr'
	new_comment.message = comment_text
	new_comment.for_reject = True
	new_comment.save()
	delivery.comments.add(new_comment)
	if(new_comment.message == comment_text) and (delivery.status == 'rd'):
		data = {
			'result': 'success'
		}
	else:
		data = {
			'result': 'failed'
		}
	data = json.dumps(data)
	return HttpResponse(data, content_type='application/json')


def set_auto_dispatch_on(request):
	courier_id = request.GET.get("courier-id", None)
	result = cp.set_auto_dispatch(courier_id)
	if result:
		courier = Courier.objects.get(id=courier_id)
		courier_name = courier.user.get_username()
		data = {
			'courier_name': courier_name
		}
	else:
		data = ""
	data = json.dumps(data)
	return HttpResponse(data, content_type='application/json')


def set_auto_dispatch_off(request):
	cp.unset_auto_dispatch()
	data = {}
	data['result'] = 'success' if not cp.auto_dispatch else 'failure'
	data = json.dumps(data)
	return HttpResponse(data, content_type='application/json')


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# $$$$$  Courier  section $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def courier_home(request):
	courier = Courier.objects.get(user=request.user)
	deliveries = Delivery.objects.filter(Q(status='ap'), courier=courier)
	context = {
		'target_tasks': deliveries
	}

	return render(request, "courier-home.html", context)


def courier_tasks(request):
	courier = Courier.objects.get(user=request.user)
	context = {
		'courier': courier
	}
	return render(request, "courier-tasks.html", context)


def courier_delivered(request):
	context = {
		'courier': 'test'
	}
	return render(request, "courier-delivered.html", context)


def courier_tasks_smart_sort(request):
	context = {
		'd': "d"
	}
	return render(request, "courier-tasks-smart-sort.html", context)


def courier_tasks_custom_sort(request):
	context = {
		'd': "d"
	}
	return render(request, "courier-tasks-custom-sort.html", context)


def courier_tasks_should_pickup(request):
	deliveries = Delivery.objects.filter(courier=Courier.objects.get(user=request.user), status='wp')
	courier = Courier.objects.get(user=request.user)
	context = {
		'deliveries': deliveries,
		'courier': courier
	}
	return render(request, "courier-tasks-should-pickup.html", context)


def courier_tasks_pickedup(request):
	courier = Courier.objects.get(user=request.user)
	deliveries = Delivery.objects.filter(courier=courier).exclude(status='ap')
	pickedup_count = 0
	for delivery in deliveries:
		packages = Package.objects.filter(delivery=delivery, status='p')
		pickedup_count += packages.count()
	context = {
		'pickedup_deliveries': deliveries,
		'pickedup_count': pickedup_count,
		'courier': courier,
	}
	return render(request, "courier-tasks-pickedup.html", context)


rejected_package_ids = []


def courier_tasks_rejected_pickup(request):
	courier = Courier.objects.get(user=request.user)
	today = datetime.now().date()
	deliveries_today = Delivery.objects.filter(courier=courier, request_time_created__gte=today).exclude(status="ap")
	context = {
		'deliveries_today': deliveries_today,
		'courier': courier
	}
	return render(request, "courier-tasks-reject-pickup.html", context)


def failure_tasks(request):
	today = datetime.now().date()
	yesterday = today - timedelta(1)
	courier = Courier.objects.get(user=request.user)
	deliveries = Delivery.objects.filter(courier=courier, request_time_created__gte=yesterday)
	package_list = []
	for delivery in deliveries:
		for package in delivery.package_set.all():
			if package.status == "hf":
				package_list.append(package)
	context = {
		'courier': courier,
		'deliveries': deliveries,
		'package_list': package_list
	}
	return render(request, "courier-tasks-failures.html", context)


def pickup_rejected(request):
	package_id = request.GET.get("packageId", None)
	package = Package.objects.get(id=package_id)
	package_intial_status = package.status
	package.set_status_by_action("pickup_rejected")
	data = {}
	if package.status != package_intial_status:
		data['result'] = "success"
	else:
		data['result'] = "failure"
	data = json.dumps(data)
	return HttpResponse(data, content_type='application/json')


def courier_target_task(request):
	courier = Courier.objects.get(user=request.user)
	deliveries = Delivery.objects.filter(courier=courier)
	context = {
		'deliveries': deliveries,
		'courier_has_target_item': courier.has_item_in_target_tasks(),
		'courier': courier
	}
	return render(request, "courier-target-task.html", context)


def put_task_on_target(request):
	task_goal = request.GET.get('task-goal', None)
	if task_goal == 'pickup':
		delivery_id = request.GET.get('id', None)
		delivery = Delivery.objects.get(id=delivery_id)
		delivery.set_status_by_action("add_to_pickup_target", request.user.role)
		delivery.save()
		updated_delivery = Delivery.objects.get(id=delivery_id)
		if updated_delivery.status == 'ap':
			data = {'status': 'success'}
		else:
			data = {'status': 'failed'}
	elif task_goal == 'handover':
		package_id = request.GET.get('id', None)
		package = Package.objects.get(id=package_id)
		package.set_status_by_action("add_to_handover_target")
		package.save()
		updated_package = Package.objects.get(id=package_id)
		if updated_package.status == 'ah':
			data = {'status': 'success'}
		else:
			data = {'status': 'failed'}
	data = json.dumps(data)
	return HttpResponse(data, content_type='application/json')


def withdraw_target_task(request):
	id = request.GET.get('id', None)
	item_type = request.GET.get('item-type', None)
	if item_type == 'delivery':
		delivery_id = id
		delivery = Delivery.objects.get(id=delivery_id)
		initial_delivery_status = delivery.status
		delivery.set_status_by_action("undo_add_to_pickup_target", request.user.role)
		delivery.save()
		updated_delivery = Delivery.objects.get(id=delivery_id)
		if updated_delivery.status != initial_delivery_status:
			data = {'status': 'success'}
		else:
			data = {'status': 'failed'}
	elif item_type == 'package':
		package_id = id
		package = Package.objects.get(id=package_id)
		package.set_status_by_action("undo_add_to_handover_task")
		package.save()
		updated_package = Package.objects.get(id=package_id)
		if updated_package.status == 'p':
			data = {'status': 'success'}
		else:
			data = {'status': 'failed'}
	data = json.dumps(data)
	return HttpResponse(data, content_type='application/json')


def check_db_for_courier(request):
	courier = Courier.objects.get(user=request.user)
	data = {
		'hasCourierNewTask': cp.has_courier_new_task(courier.id)
	}
	data = json.dumps(data)
	return HttpResponse(data, content_type='application/json')


def unset_new_task_for_courier(request):
	courier = Courier.objects.get(user=request.user)
	cp.unset_new_task_for_courier(courier.id)
	if not cp.has_courier_new_task(courier.id):
		data = {'result':'success'}
	else:
		data = {'result': 'failure'}
	data = json.dumps(data)
	return HttpResponse(data, content_type='application/json')


def reject_package_pickup(request):
	package_id = request.GET.get('packageId', None)
	rejection_reason = request.GET.get('rejectionReason', None)
	package = Package.objects.get(id=package_id)
	package.set_status_by_action("reject_pickup")
	package.save()
	comment = Comment()
	comment.user = request.user
	comment.set_actor(request)
	comment.for_reject = True
	comment.reason = 'pr'
	comment.message = rejection_reason
	comment.save()
	package.comments.add(comment)
	if package.comments.get(pk=comment.id).message == rejection_reason:
		data = {'result':'success'}
	else:
		data = {'result':'failed'}
	data = json.dumps(data)
	return HttpResponse(data, content_type='application/json')


def undo_reject_package_pickup(requst):
	comment_id = requst.GET.get('commentId', None)
	package_id = requst.GET.get('packageId', None)
	Comment.objects.get(id=comment_id).delete()
	package = Package.objects.get(id=package_id)
	package.set_status_by_action("undo_reject_pickup")
	package.save()
	updated_package = Package.objects.get(id=package_id)
	if not Comment.objects.filter(id=comment_id).exists() and updated_package.status == 'ap':
		data = {'result': 'success'}
	else:
		data = {'result': 'failed'}
	data = json.dumps(data)
	return HttpResponse(data, content_type='application/json')


def do_undo_pickup(request):
	package_id = request.GET.get("packageId", None)
	action = request.GET.get("action", None)
	package = Package.objects.get(id=package_id)
	initial_state = package.status
	if action == "do":
		package.set_status_by_action("pickup")
		package.save()
	elif action == "undo":
		package.set_status_by_action("undo_pickup")
		package.save()
	current_state = Package.objects.get(id=package_id).status
	if initial_state != current_state:
		data = {"result": 'success'}
	else:
		data = {"result": 'failed'}
	data = json.dumps(data)
	return HttpResponse(data, content_type='application/json')


def done_width_pickup(request):
	delivery_id = request.GET.get("deliveryId", None)
	delivery = Delivery.objects.get(id=delivery_id)
	initial_delivery_status = delivery.status
	delivery.set_status_by_action("done_with_pickup", request.user.role)
	delivery.save()
	if initial_delivery_status != delivery.status:
		set_pickup_time(delivery_id)
		data = {'result':'success'}
	else:
		data = {'result':'failed'}
	data = json.dumps(data)
	return HttpResponse(data, content_type='application/json')

def report_failure(request):
	item_id = request.GET.get("id", None)
	comment_text = request.GET.get("commentText", None)
	action = request.GET.get("action", None)
	data = {}
	if action == "report-pickup-failure":
		try:
			delivery = Delivery.objects.get(id=item_id)
			comment = Comment()
			comment.user = request.user
			comment.set_actor(request)
			comment.reason = "pf"
			comment.message = comment_text
			comment.save()
			delivery.set_status_by_action("report_pickup_failure", request.user.role)
			delivery.save()
			delivery.comments.add(comment)
			data['result'] = "success"
		except Delivery.DoesNotExist:
			data['result'] = "failure"
	elif action == "report-handover-failure":
		try:
			package = Package.objects.get(id=item_id)
			comment = Comment()
			comment.user = request.user
			comment.set_actor(request)
			comment.reason = "hf"
			comment.message = comment_text
			comment.save()
			package.set_status_by_action("report_handover_failure")
			package.save()
			package.comments.add(comment)
			data['result'] = "success"
		except Package.DoesNotExist:
			data['result'] = "failure"
	data = json.dumps(data)

	return HttpResponse(data, content_type='application/json')


def handover_package(request):
	package_id = request.GET.get("packageId", None)
	signer_name = request.GET.get("signerName", None)
	signer_phone = request.GET.get("signerPhone", None)
	package = Package.objects.get(id=package_id)
	if signer_name:
		package.signer_name = signer_name
	if signer_phone:
		package.signer_phone = signer_phone
	package.set_status_by_action("handover")
	package.handover_time = datetime.now()
	package.save()
	updated_package = Package.objects.get(id=package_id)
	if updated_package.status == "d":
		data = {"result": "success"}
	else:
		data = {"result": "failed"}
	data = json.dumps(data)
	return HttpResponse(data, content_type='application/json')


def add_failure_task_to_target(request):
	item_id = request.GET.get('item_id', None)
	item_type = request.GET.get('item_type', None)
	data = {}
	if item_type == 'delivery':
		delivery = Delivery.objects.get(id=item_id)
		delivery_initial_status = delivery.status
		delivery.set_status_by_action("add_to_pickup_target", request.user.role)
		delivery.save()
		if delivery.status != delivery_initial_status:
			data['result'] = "success"
		else:
			data['result'] = "failure"
	elif item_type == "package":
		package = Package.objects.get(id=item_id)
		package_initial_status = package.status
		package.set_status_by_action("add_to_handover_target")
		if package.status != package_initial_status:
			data['result'] = "success"
		else:
			data['result'] = "failure"
	data = json.dumps(data)
	return HttpResponse(data, content_type='application/json')


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# $$$$$  Helper functions section $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def add_address(address_data, user, category='da'):
	if 'title' in address_data.keys():
		print("Add address path point 1")
		pass
	else:
		print("Add address path point 2")
		address_data['title'] = None
	result = {}
	address = Address()
	address.user = user
	address.category = category
	address.city = City.objects.get(id=address_data["city"])
	address.address1 = address_data["address1"]
	address.address2 = address_data["address2"]
	address.zip = address_data["zip"]
	address.phone = address_data["phone"]
	address.fax = address_data["fax"]
	address.email = address_data["email"]
	address.hash = address.get_one_line_hash()
	try:
		address = Address.objects.get(user=user, hash=address.hash)
		print("Add address path point 3")
		if address.archived:
			print("Add address path point 4")
			if address_data['title']:
				print("Add address path point 5")
				try:
					address = Address.objects.get(user=user, title=address_data['title'].lower())
					print("Add address path point 6")
					result['address'] = address
					result['error-type'] = "duplicateTitle"
					result['error-message'] = "This title has already used for address with ID of {}".format(address.id)
					return result
				except Address.DoesNotExist:
					print("Add address path point 7")
					address.title = address_data['title'].lower()
					address.archived = False
					address.save()
					result['address'] = address
					result['error-type'] = ""
					result['error-message'] = ""
					return result
			else:
				print("Add address path point 8")
				address.archived = False
				address.save()
				result['address'] = address
				result['error-type'] = ""
				result['error-message'] = ""
				return result
		else:
			print("Add address path point 9")
			result['address'] = address
			result['error-type'] = "duplicateAddress"
			result['error-message'] = "This address is already exists! address ID: {}".format(address.id)
			return result
	except Address.DoesNotExist:
		print("Add address path point 10")
		if address_data['title']:
			print("Add address path point 11")
			try:
				address = Address.objects.get(user=user, title=address_data['title'].lower())
				print("Add address path point 12")
				result['address'] = address
				result['error-type'] = "duplicateTitle"
				result['error-message'] = "This title has already used for address with ID of {}".format(address.id)
				return result
			except Address.DoesNotExist:
				print("Add address path point 13")
				address.title = address_data['title'].lower()
				address.save()
				result['address'] = address
				result['error-type'] = ""
				result['error-message'] = ""
				return result
		else:
			print("Add address path point 14")
			address.save()
			result['address'] = address
			result['error-type'] = ""
			result['error-message'] = ""
			return result


def update_address(address_data, user):
	if address_data['title']:
		address_data['title'] = address_data['title'].lower()
	result = {}
	address = Address()
	address.user = user
	address.city = City.objects.get(id=address_data["city"])
	address.address1 = address_data["address1"]
	address.address2 = address_data["address2"]
	address.zip = address_data["zip"]
	address.phone = address_data["phone"]
	address.fax = address_data["fax"]
	address.email = address_data["email"]
	address.hash = address.get_one_line_hash()
	try:
		old_address = Address.objects.get(id=address_data['address-id'], user=user)
		print("Path point: 1")
		if old_address.hash == address.hash:
			print("Path point: 2")
			if old_address.title == address_data['title']:
				return
			else:
				print("Path point: 3")
				if address_title_used(user, address_data['title']):
					returned_address = address_title_used(user, address_data['title'])
					print("Path point: 3.1")
					result['address'] = returned_address
					result['error-type'] = "duplicateTitle"
					result['error-message'] = "This title has already used for address with ID of {}".format(returned_address.id)
					return result
				else:
					print("Path point: 4")
					old_address.title = address_data['title']
					old_address.save()
					result['address'] = old_address
					result['error-type'] = ""
					result['error-message'] = ""
					return result
		else:
			print("Path point: 5")
			if old_address.is_referenced():
				print("Path point: 5.1")
				old_address_old_title = old_address.title
				old_address.title = None
				old_address.archived = True
				old_address.save()
				add_result = add_address(address_data, user)
				print(add_result['error-type'])
				if not add_result['error-type']:
					print("Path point: 6")
					result['address'] = add_result['address']
					result['error-type'] = ""
					result['error-message'] = ""
					return result
				else:
					old_address.title = old_address_old_title
					old_address.archived = False
					old_address.save()
					print("Path point: 7")
					result['address'] = add_result['address']
					result['error-type'] = add_result['error-type']
					result['error-message'] = add_result['error-message']
					return result
			else:
				print("Path point: 8")
				result_address = address_title_used(user, address_data['title'])
				if result_address and result_address != old_address:
					print("Path point: 8.1")
					result['address'] = address
					result['error-type'] = "duplicateTitle"
					result['error-message'] = "This title has already used for address with ID of {}".format(old_address.id)
					return result
				else:
					print("Path point: 9")
					try:
						address = Address.objects.get(user=user, hash=address.hash)
						print("Path point: 10")
					except Address.DoesNotExist:
						print("Path point: 11")
						old_address.title = address_data['title'].lower()
						old_address.city = City.objects.get(id=address_data["city"])
						old_address.address1 = address_data["address1"]
						old_address.address2 = address_data["address2"]
						old_address.zip = address_data["zip"]
						old_address.phone = address_data["phone"]
						old_address.fax = address_data["fax"]
						old_address.email = address_data["email"]
						old_address.hash = address.get_one_line_hash()
						old_address.save()
						result['address'] = old_address
						result['error-type'] = ""
						result['error-message'] = ""
						return result
	except Address.DoesNotExist:
		result['address'] = ""
		result['error-type'] = "noAddress"
		result['error-message'] = "Address not found!"
		return result


def delete_address(address_id, user):
	try:
		address = Address.objects.get(id=address_id, user=user)
		if address.is_referenced():
			address.title = None
			address.archived = True
			address.save()
			return True
		else:
			address.delete()
			return True
	except Address.DoesNotExist:
		return False


def address_title_used(user, title):
	title = title.lower()
	try:
		address = Address.objects.get(user=user, title=title)
		return address
	except Address.DoesNotExist:
		return None


def set_pickup_time(delivery_id):
	delivery = Delivery.objects.get(id=delivery_id)
	for package in Package.objects.filter(delivery=delivery):
		if package.status == 'pc':
			package.pickup_time = datetime.now()
			package.save()


def zone_division_name():
	from settings.models import ZoneSystem
	zone_system = ZoneSystem.objects.all().first()
	return zone_system.get_name_display()


def get_country_province_city_list(city_id):
	city = City.objects.get(id=city_id)
	cities = City.objects.filter(province=city.province)
	province = Province.objects.get(id=city.province.id)
	provinces = Province.objects.filter(country=province.country)
	countries = Country.objects.all()
	data = {
		'countries': {},
		'selected-country-id': '',
		'provinces': {},
		'selected-province-id': '',
		'cities': {},
		'selected-city-id': ''
	}
	for country in countries:
		data['countries'][country.id] = country.name.capitalize()
	if len(data['countries']) > 1:
		data['countries'][0] = 'Select country ...'
	data['selected-country-id'] = province.country.id
	for province in provinces:
		data['provinces'][province.id] = province.name.capitalize()
	if len(data['provinces']) > 1:
		data['provinces'][0] = 'Select province ...'
	data['selected-province-id'] = city.province.id
	for city in cities:
		data['cities'][city.id] = city.name.capitalize()
	if len(data['cities']) > 1:
		data['cities'][0] = 'Select city ...'
	data['selected-city-id'] = city_id
	return data


# ---------------------------------------------------------------------------
# This is for testing perpose on develepment phase
# Let this part remain at the bottom
# TODO: remove this function and associated parts and pages on remote server


def test_page(request):
	package = Package.objects.get(id=16)
	delivery = package.delivery
	context = {
		'x': delivery
	}
	return render(request, "test-page.html", context)