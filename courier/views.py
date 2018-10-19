from django.shortcuts import render, redirect
from courier.models import Dispatcher, Courier, Address, ServiceType, PackageTemplate, AddressBook, Comment
from courier.models import Delivery, Package
from django.contrib.auth.models import User
from account.models import Profile
from datetime import datetime, timedelta, time
import json
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q


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
			package = Package.objects.get(tracking_id=code)
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

	context = {
		"addressBook": address_book,
		'service_types': service_types,
		'package_templates': package_templates,
	}
	return render(request, "user-delivery.html", context)


def user_address_book(request):
	address_book = AddressBook.objects.filter(user=request.user)
	context = {
		"address_book": address_book
	}
	return render(request, "user-address-book.html", context)


def user_add_address(request):
	from .forms import AddressBookForm, AddressForm
	if request.method == "POST":
		address_book_form = AddressBookForm(request.POST, request.FILES)
		address_form = AddressForm(request.POST, request.FILES)
		if address_book_form.is_valid() and address_form.is_valid():
			address_book_obj = address_book_form.save(commit=False)
			address_obj = address_form.save()
			address_book_obj.address = address_obj
			address_book_obj.user = request.user
			address_book_obj.save()
			return redirect("user_address_book")
	else:
		address_book_form = AddressBookForm()
		address_form = AddressForm()
	context = {
		'address_book_form': address_book_form,
		'address_form': address_form
	}
	return render(request, "user-add-address.html", context)


def user_edit_address(request, slug):
	from .forms import AddressForm, AddressBookForm
	if request.method == "POST":
		try:
			address_book = AddressBook.objects.get(id=slug, user=request.user)
			address = Address.objects.get(id=address_book.address_id)
			address_book_form = AddressBookForm(request.POST, instance=address_book)
			address_form = AddressForm(request.POST, instance=address)
			if address_book_form.is_valid() and address_form.is_valid():
				address_form.save()
				address_book_form.save()
				return redirect("user_address_book")
		except AddressBook.DoesNotExist:
			return redirect("user_address_book")
	else:
		try:
			address_book = AddressBook.objects.get(id=slug, user=request.user)
			address = Address.objects.get(id=address_book.address_id)
			address_book_form = AddressBookForm(instance=address_book)
			address_form = AddressForm(instance=address)
		except AddressBook.DoesNotExist:
			return redirect("user_address_book")

	context = {
		'address_form': address_form,
		'address_book_form': address_book_form
	}
	return render(request, "user-edit-address.html", context)


def user_delete_address(request, slug):
	try:
		address_book = AddressBook.objects.get(id=slug, user=request.user)
		address_book.delete()
		return redirect("user_address_book")
	except AddressBook.DoesNotExist:
		return redirect("user_address_book")


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


def get_user_address(request):
	id = request.GET.get('id', None)
	addr = Address.objects.get(id=id)
	data = {
		'state': addr.state,
		'city': addr.city,
		'address1': addr.address1,
		'address2': addr.address2,
		'zip': addr.zip,
		'phone': addr.phone,
		'fax': addr.fax,

	}
	data = json.dumps(data)
	return HttpResponse(data, content_type='application/json')


def submit_user_delivery(request):
	from django.urls import reverse
	try:
		delivery_str = request.GET.get('delivery', None)
		delivery_data = json.loads(delivery_str)
		delivery = Delivery()
		# Set .from_address in delivery
		delivery.from_address = get_set_address(delivery_data["source_address"], request.user,'s')
		# Set .status
		delivery.status = "wd"
		# Set .payment_type
		delivery.payment_type = "os"
		# Set .service_type
		delivery.service_type = ServiceType.objects.get(pk=delivery_data["service_type"])
		package_data = {}
		delivery.save()
		for package_index in delivery_data["packages"]:
			package_data = delivery_data["packages"][package_index]
			package = Package()
			delivery_address = get_set_address(package_data, request.user, 'd')
			package.to_address = delivery_address
			template_id = package_data["template_id"]
			package.template = PackageTemplate.objects.get( pk=template_id )
			package.signature = package_data["signature"]
			package.delivery = delivery
			package.save()
		delivery.user = request.user
		delivery.save()
		result = {"status": "success", "redirect": request.build_absolute_uri(reverse('user_tracking'))}
	except:
		result = {"status": "error"}
	return HttpResponse(json.dumps(result), content_type='application/json')


def delivery_item(request, slug):
	delivery = Delivery.objects.get(tracking_id=slug)
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

	context = {
		'couriers': couriers_info,
		'deliveries_to_handle': deliveries_to_handle,
		'reviewed_deliveries': reviewed_deliveries
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
	new_comment.actor = get_actor_letter(request)
	new_comment.user = request.user
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
	context = {
		'courier': 'tasks'
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
	context = {
		'deliveries': deliveries
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
	}
	return render(request, "courier-tasks-pickedup.html", context)

rejected_package_ids = []
def courier_tasks_rejected_pickup(request):
	courier = Courier.objects.get(user=request.user)
	deliveries = Delivery.objects.filter(courier=courier)
	context = {
		'deliveries': deliveries
	}
	return render(request, "courier-tasks-reject-pickup.html", context)


def courier_target_task(request):
	courier = Courier.objects.get(user=request.user)
	deliveries = Delivery.objects.filter(Q(status='ap') | Q(status='pc') | Q(status='pp'), courier=courier)
	package_statistics = {}
	target_items_count = 0
	for delivery in deliveries:
		if delivery.status == 'ap':
			target_items_count += 1
		unhandled = 0
		picked = 0
		rejected = 0
		packages = Package.objects.filter(delivery=delivery)
		total = packages.count()
		for package in packages:
			if package.status == 'ah':
				target_items_count += 1
			status = package.status
			if status == 'wp':
				unhandled += 1
			elif status == 'pc':
				picked += 1
			elif status == 'rc':
				rejected += 1
		package_statistics[delivery.id] = {'total': total, 'unhandled': unhandled, 'picked': picked, 'rejected': rejected}
	context = {
		'target_pickup_deliveries': deliveries,
		'packages': packages,
		'package_statistics': package_statistics,
		'target_items_count': target_items_count
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
	try:
		request_count = Delivery.objects.filter(courier=courier, status='wc').count()
		data = {
			'request_count': request_count,
		}
	except Delivery.DoesNotExist:
		data = {
			'last_delivery_id': 0,
		}
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
	comment.actor = get_actor_letter(request)
	comment.for_reject = True
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
	result = Comment.objects.get(id=comment_id).delete()
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
	comment.actor = get_actor_letter(request)
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
	address.state = address_data["state"]
	address.city = address_data["city"]
	address.address1 = address_data["address1"]
	address.address2 = address_data["address2"]
	address.zip = address_data["zip"]
	address.phone = address_data["phone"]
	address.fax = address_data["fax"]
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


def get_actor_letter(request):
	if request.user.is_authenticated:
		if Courier.objects.filter(user=request.user).exists():
			return 'c'
		elif Dispatcher.objects.filter(user=request.user).exists():
			return 'd'
		else:
			return 'u'
	else:
		return 'v'


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


# ---------------------------------------------------------------------------
# This is for testing perpose on develepment phase
# Let this part remain at the bottom
# TODO: remove this function and associated parts and pages on remote server


def test_page(request):
	courier = Courier.objects.get(user=request.user)
	deliveries = Delivery.objects.filter(Q(status='ap') | Q(packages__status='ah'), courier = courier)
	context = {
		'target_tasks': deliveries
	}
	return render(request, "test-page.html", context)
