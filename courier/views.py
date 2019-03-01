from django.shortcuts import render, redirect
from courier.models import Dispatcher, Courier, Address, ServiceType, PackageTemplate, AddressBook,\
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
			return render(request, "user-home.html", context)
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
	# TODO: get Delivery with same user as request.user
	deliveries = Delivery.objects.filter(user=request.user)
	context = {
		'deliveries': deliveries,
		'users': 'test',
	}
	return render(request, "user-tracking.html", context)


def user_delivery(request):
	service_types = ServiceType.objects.all()
	package_templates = PackageTemplate.objects.all()
	address_book = AddressBook.objects.filter(user=request.user)
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
		"addressBook": address_book,
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
	address_book = AddressBook.objects.filter(user=request.user)
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
		"address_book": address_book,
		"countries": countries,
		"provinces": provinces,
		"cities": cities,
		'zone_division_name': zone_division_name()
	}
	return render(request, "user-address-book.html", context)


def add_update_user_address(request):
	action = request.GET.get('action', None);
	address_book_id = request.GET.get('address-book-id', None)
	city = City.objects.get(id=request.GET.get('city', None))
	errors = []
	if action == "add":
		x = AddressBook.objects.filter(user=request.user)
		address_book = AddressBook()
		address_book.user = request.user
		address = Address()
	elif action == "update":
		address_book = AddressBook.objects.get(id=address_book_id)
		if address_book.user != request.user:
			return
		else:
			address = Address.objects.get(id=address_book.address.id)
	address.city = city
	address.address1 = request.GET.get('address1', None)
	address.address2 = request.GET.get('address2', None)
	address.zip = request.GET.get('zip', None)
	address.phone = request.GET.get('phone', None)
	address.fax = request.GET.get('fax', None)
	address.email = request.GET.get('email', None)
	address.save()
	address_book.address = address
	address_book.title = request.GET.get('title', None).lower()
	address_book.used_for = 'd'
	try:
		address_book.save()
	except IntegrityError as e:
		errors.append(f'Already have an address with title: {request.GET.get("title", None)}')
	data = {
		'errors': errors
	}
	data = json.dumps(data)
	return HttpResponse(data, content_type='application/json')


def get_user_address(request):
	address_book_id = request.GET.get('addressBook_id', None);
	address_book = AddressBook.objects.get(id=address_book_id)
	if address_book.user == request.user:
		address = Address.objects.get(id=address_book.address.id)
		data = get_country_province_city_list(address.city.id)
		if address_book.title:
			data['title'] = address_book.title.capitalize()
		else:
			data['title'] = ""
		data['address1'] = address.address1
		data['address2'] = address.address2
		data['zip'] = address.zip
		data['phone'] = address.phone
		data['fax'] = address.fax
		data['email'] = address.email
	else:
		data = {}
	data = json.dumps(data, sort_keys=True)
	return HttpResponse(data, content_type='application/json')


def delete_user_address(request):
	address_book_id = request.GET.get("address_book_id", None)
	data = {}
	try:
		address_book = AddressBook.objects.get(id=address_book_id, user=request.user)
		address_book.delete()
		data['result'] = 'success'
	except AddressBook.DoesNotExist:
		data['result'] = 'failed'
	data = json.dumps(data);
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
	try:
		delivery_str = request.GET.get('delivery', None)
		delivery_data = json.loads(delivery_str)
		delivery = Delivery()
		delivery.user = request.user
		delivery.status = "wd"
		if cp.auto_dispatch:  # If auto dispatch is on sets the delivery courier to intended courier
			delivery.courier = Courier.objects.get(id=cp.auto_dispatch_courier.id)
			cp.set_new_task_for_courier(cp.auto_dispatch_courier.id)
			delivery.status = "wc"
		delivery.from_address = get_set_address(delivery_data["source_address"], request.user,'s')
		delivery.payment_type = "os"
		delivery.service_type = ServiceType.objects.get(pk=delivery_data["service_type"])
		package_data = {}
		delivery.save()
		for package_index in delivery_data["packages"]:
			package_data = delivery_data["packages"][package_index]
			package = Package()
			package.to_address = get_set_address(package_data, request.user, 'd')
			package.template = PackageTemplate.objects.get(pk=package_data["template_id"])
			package.signature = package_data["signature"]
			package.tracking_code_sharing_sms = package_data["share_tracking_sms"]
			package.tracking_code_sharing_email = package_data["share_tracking_email"]
			package.description = package_data["description"]
			package.delivery = delivery
			package.save()
		result = {"status": "success", "redirect": request.build_absolute_uri(reverse('user_tracking'))}
	except BaseException as e:
		result = {"status": "error", "message": e}
	return HttpResponse(json.dumps(result), content_type='application/json')


def delivery_item(request, slug):
	delivery = Delivery.objects.get(id=slug)
	packages = Package.objects.filter(delivery=delivery)
	context = {
		"delivery": delivery,
		"packages": packages
	}
	return render(request, "user-delivery-report.html", context)


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

	deliveries_count = Delivery.objects.all().exclude(Q(status='rd',request_time_created__lte=today) | Q(status='rc',request_time_created__lte=today) | Q(status='d',request_time_created__lte=today)).count()
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
		user_img_path = "/files/{}".format(Profile.objects.get(user=user).avatar)
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
		'dispatcher': 'test'
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
	delivery.status = 'wc'
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
	delivery.status = 'rd'
	delivery.dispatcher = dispatcher
	delivery.save()
	new_comment = Comment()
	new_comment.set_actor(request)
	new_comment.user = request.user
	new_comment.reason = 'dr'
	new_comment.message = comment_text
	new_comment.for_reject = True
	new_comment.save()
	delivery.comment.add(new_comment)
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
	result = json.dumps(result)
	return HttpResponse(result, content_type='application/json')


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
	deliveries = Delivery.objects.filter(courier=Courier.objects.get(user=request.user), status='wc')
	courier = Courier.objects.get(user=request.user)
	context = {
		'deliveries': deliveries,
		'courier': courier
	}
	return render(request, "courier-tasks-should-pickup.html", context)


def courier_tasks_pickedup(request):
	courier = Courier.objects.get(user=request.user)
	deliveries = Delivery.objects.filter(Q(status='pc') | Q(status='pp'), courier=courier)
	pickedup_count = 0
	for delivery in deliveries:
		packages = Package.objects.filter(delivery=delivery)
		for package in packages:
			if package.status == 'pc':
				pickedup_count += 1
	context = {
		'pickedup_deliveries': deliveries,
		'pickedup_count': pickedup_count,
		'courier': courier,
	}
	return render(request, "courier-tasks-pickedup.html", context)


rejected_package_ids = []


def courier_tasks_rejected_pickup(request):
	courier = Courier.objects.get(user=request.user)
	deliveries = Delivery.objects.filter(courier=courier)
	context = {
		'deliveries': deliveries,
		'courier': courier
	}
	return render(request, "courier-tasks-reject-pickup.html", context)


def courier_target_task(request):
	courier = Courier.objects.get(user=request.user)
	deliveries = Delivery.objects.filter(Q(status='ap') | Q(status='pc') | Q(status='pp'), courier=courier)
	context = {
		'deliveries': deliveries,
		'courier_has_target_item': courier.has_item_in_target_tasks(),
	}
	return render(request, "courier-target-task.html", context)


def put_task_on_target(request):
	task_goal = request.GET.get('task-goal', None)
	if task_goal == 'pickup':
		delivery_id = request.GET.get('id', None)
		delivery = Delivery.objects.get(id=delivery_id)
		delivery.status = 'ap'
		delivery.save()
		updated_delivery = Delivery.objects.get(id=delivery_id)
		if updated_delivery.status == 'ap':
			data = {'status': 'success'}
		else:
			data = {'status': 'failed'}
	elif task_goal == 'handover':
		package_id = request.GET.get('id', None)
		package = Package.objects.get(id=package_id)
		package.status = 'ah'
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
		delivery.status = 'wc'
		delivery.save()
		sync_delivery_packages_status(delivery_id)
		updated_delivery = Delivery.objects.get(id=delivery_id)
		if updated_delivery.status == 'wc':
			data = {'status': 'success'}
		else:
			data = {'status': 'failed'}
	elif item_type == 'package':
		package_id = id
		package = Package.objects.get(id=package_id)
		package.status = 'pc'
		package.save()
		updated_package = Package.objects.get(id=package_id)
		if updated_package.status == 'pc':
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
	package.status = 'rc'
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
	package.status = 'wp'
	package.save()
	updated_package = Package.objects.get(id=package_id)
	if not Comment.objects.filter(id=comment_id).exists() and updated_package.status == 'wp':
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
		package.status = 'pc'
		package.save()
	elif action == "undo":
		package.status = 'wp'
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
	initial_delivery_status = Delivery.objects.get(id=delivery_id).status
	sync_delivery_packages_status(delivery_id)
	current_delivery_status = Delivery.objects.get(id=delivery_id).status
	if initial_delivery_status != current_delivery_status :
		set_pickup_time(delivery_id)
		data = {'result':'success'}
	else:
		data = {'result':'failed'}
	data = json.dumps(data)
	return HttpResponse(data, content_type='application/json')


def carry_back_package(request):
	package_id = request.GET.get("packageId", None)
	comment_text = request.GET.get("commentText", None)
	package = Package.objects.get(id=package_id)
	package.status = "ca"
	package.save()
	comment = Comment()
	comment.user = request.user
	comment.set_actor(request)
	comment.message = comment_text
	comment.save()
	package.comments.add(comment)
	if package.comments.get(pk=comment.id).message == comment_text:
		data = {"result": "success"}
	else:
		data = {"result": "failed"}
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
	package.status = "d"
	package.handover_time = datetime.now()
	package.save()
	updated_package = Package.objects.get(id=package_id)
	if updated_package.status == "d":
		data = {"result": "success"}
		sync_delivery_packages_status_1(package_id)
	else:
		data = {"result": "failed"}
	data = json.dumps(data)
	return HttpResponse(data, content_type='application/json')


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# $$$$$  Helper functions section $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def get_set_address(address_data, user, usage):
	address = Address()
	address.city = City.objects.get(id=address_data["city"])
	address.address1 = address_data["address1"]
	address.address2 = address_data["address2"]
	address.zip = address_data["zip"]
	address.phone = address_data["phone"]
	address.fax = address_data["fax"]
	address.email = address_data["email"]
	address_hash = address.get_one_line_hash()
	try:
		address_from_db = Address.objects.get(hash=address_hash)
		package_address = address_from_db
		if not AddressBook.objects.filter(user=user, address=address_from_db).exists():
			address_book = AddressBook()
			address_book.user = user
			address_book.address = address_from_db
			address_book.used_for = usage
			address_book.save()
	except Address.DoesNotExist:
		address.save()
		address_book = AddressBook()
		address_book.user = user
		address_book.address = address
		address_book.used_for = usage
		address_book.save()
		package_address = address
	return package_address


def sync_delivery_packages_status(delivery_id):
	delivery = Delivery.objects.get(id=delivery_id)
	delivery_status = delivery.status
	if delivery_status == 'ap':
		packages = Package.objects.filter(delivery=delivery)
		package_count = packages.count() if packages.count() else 0
		pickedup_packages_count = packages.filter(status='pc').count() if packages.filter(status='pc').count() else 0
		rejected_packages_count = packages.filter(status='rc').count() if packages.filter(status='rc') else 0
		if package_count == pickedup_packages_count:
			delivery.status = 'pc'
			delivery.save()
		elif package_count == rejected_packages_count:
			delivery.status = 'rc'
			delivery.save()
		elif package_count == (rejected_packages_count + pickedup_packages_count ):
			delivery.status = 'pp'
			delivery.save()
	elif delivery_status == 'wc':
		for package in Package.objects.filter(delivery=delivery):
			package.status = 'wp'
			package.save()
			for comment in package.comments.all():
				if comment.for_reject or (comment.actor == 'c'):
					comment.delete()


def set_pickup_time(delivery_id):
	delivery = Delivery.objects.get(id=delivery_id)
	for package in Package.objects.filter(delivery=delivery):
		if package.status == 'pc':
			package.pickup_time = datetime.now()
			package.save()


def sync_delivery_packages_status_1(package_id):
	package = Package.objects.get(id=package_id)
	delivery = Delivery.objects.get(id=package.delivery.id)
	total_packages_count = Package.objects.filter(delivery=delivery).exclude(status="rc").count()
	carry_back_count = Package.objects.filter(Q(status="ca") | Q(status="c"), delivery=delivery).count()
	handover_count = Package.objects.filter(delivery=delivery, status="d").count()
	if total_packages_count == carry_back_count + handover_count:
		if total_packages_count == handover_count:
			delivery.status = "d"
		elif total_packages_count == carry_back_count:
			delivery.status = "ca"
		else:
			delivery.status = "pd"
		delivery.save()


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
	pass
# 	#cp.unset_new_task_for_courier(1)
	context = {
 		'x': ""#cp.auto_dispatch_courier.id
	}
	return render(request, "test-page.html", context)
# #.set_new_task_for_courier(2)