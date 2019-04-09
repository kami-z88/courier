from django.db import models
from django.contrib.auth.models import User, AnonymousUser
from settings.models import ZoneSystem
from django.utils import timezone, translation, six
from django.utils.translation import ugettext_lazy as _
from datetime import datetime, timedelta
import os

WEIGHT_METRICS = (
	('kg', 'Kilogram'),
	('lb', 'Pounds'),
)


# used to get dynamic directory based on user's id
def get_courier_photo_photo_path(instance, filename):
	name, ext = os.path.splitext(filename)
	filename = 'photo{}'.format(ext)
	return "courier_photo/{0}".format(filename)


def get_dispatcher_photo_photo_path(instance, filename):
	name, ext = os.path.splitext(filename)
	filename = 'photo{}'.format(ext)
	return "courier_photo/{0}".format(filename)

class AvailableTime(models.Model):
	WEEKDAYS = [
		(0, _("Monday")),
		(1, _("Tuesday")),
		(2, _("Wednesday")),
		(3, _("Thursday")),
		(4, _("Friday")),
		(5, _("Saturday")),
		(6, _("Sunday")),
	]
	weekday = models.IntegerField(
		choices=WEEKDAYS,
		unique=True
	)
	from_hour = models.TimeField()
	to_hour = models.TimeField()

	def __str__(self):
		return "{} from {} to {}".format(self.WEEKDAYS[self.weekday][1], self.from_hour, self.to_hour)


class ServiceType(models.Model):
	COST_TYPES = (
		('f', 'Fixed Amount'),
		('p', 'Percentage'),
	)
	title = models.CharField(_('Service Type'), max_length=120, blank=False, null=False)
	description = models.TextField(blank=True, null=True)
	always_avaialable = models.BooleanField(default=True, blank=False, null=False)
	available_time = models.ManyToManyField(AvailableTime)
	extra_cost = models.DecimalField(max_digits=6, decimal_places=2, blank=False, null=False, default=0.0)
	extra_cost_type = models.CharField(_('Extra Payment Type'), max_length=1, default='cs', choices=COST_TYPES)

	def __str__(self):
		return self.title


class Dispatcher(models.Model):
	user = models.OneToOneField(User, related_name='dispatcher', on_delete=models.CASCADE)
	photo = models.ImageField(_('If you chose "Upload Image" as photo option this image will be used.'),
							   upload_to=get_dispatcher_photo_photo_path, blank=True, null=True)


class Courier(models.Model):
	user = models.OneToOneField(User, related_name='courier', on_delete=models.CASCADE)

	def has_item_in_target_tasks(self):
		has_item = False
		deliveries = Delivery.objects.filter(courier=self)
		for delivery in deliveries:
			has_item = True if delivery.status == "ap" else  has_item
			has_item = True if delivery.status == "ah" else  has_item
			for package in delivery.package_set.all():
				has_item = True if package.status == "ah" else has_item
		return has_item

	def deliveries_to_pickup(self):
		return Delivery.objects.filter(status='ap', courier=self)

	def packages_to_handover(self):
		delivery_ids = set()
		deliveries = Delivery.objects.filter(courier=self)
		for delivery in deliveries:
			delivery_ids.add(delivery.id)
		return Package.objects.filter(delivery__in=delivery_ids, status='ah')

	def deliveries_should_pickup(self):
		return Delivery.objects.filter(courier=self, status='wp')

	def packages_pickedup(self):
		delivery_ids = set()
		deliveries = Delivery.objects.filter(courier=self)
		for delivery in deliveries:
			delivery_ids.add(delivery.id)
		return Package.objects.filter(delivery__in=delivery_ids, status='p')

	def packages_rejected(self):
		today = datetime.now().date()
		delivery_ids = set()
		deliveries = Delivery.objects.filter(courier=self, request_time_created__gte=today).exclude(status='ap')
		for delivery in deliveries:
			delivery_ids.add(delivery.id)
		return Package.objects.filter(delivery__in=delivery_ids, status='rp')

	def recent_failure_tasks_count(self):
		today = datetime.now().date()
		yesterday = today - timedelta(1)
		deliveries = Delivery.objects.filter(courier=self, request_time_created__gte=yesterday)
		count = 0
		for delivery in deliveries:
			if delivery.status == 'pf':
				count += 1
			for package in delivery.package_set.all():
				if package.status == 'hf':
					count += 1
		return count


class Payment(models.Model):
	TYPES = (
		('pt', 'Payed for transport'),  # payed online for transport when requesting it
		#('os', 'On site payment'),  # payed to courier when giving a package
		#('pd', 'Payed from deposit'),  # payed from deposit for transport when requesting it
		#('ad', 'Add to deposit'),  # payed in profile page to add money to deposit
		('cs', 'Payed using cash'),  # payed when sending package using cash
		('cd', 'Payed using card'),  # payed when sending package using bank cards
	)
	type = models.CharField(_('Status'), max_length=2, default='cs', choices=TYPES)
	payment_id = models.BigIntegerField(blank=True, null=True)
	payment_time = models.DateTimeField(auto_created=True)

	def __str__(self):
		return self.type


class OnlinePayment(models.Model):
	user = models.OneToOneField('auth.user', verbose_name=_('user'), on_delete=models.CASCADE,)
	value = models.DecimalField(max_digits=6, decimal_places=2, blank=False, null=False, default=0.0)
	meta = models.TextField(blank=False, null=False)
	def __str__(self):
		return self.value


class DepositCharge(models.Model):
	user = models.OneToOneField('auth.user', verbose_name=_('user'), on_delete=models.CASCADE,)
	value = models.DecimalField(max_digits=6, decimal_places=2, blank=False, null=False, default=0.0)
	meta = models.TextField(blank=False, null=False)


class DepositPayment(models.Model):
	user = models.OneToOneField('auth.user', verbose_name=_('user'), on_delete=models.CASCADE,)
	value = models.DecimalField(max_digits=6, decimal_places=2, blank=False, null=False, default=0.0)


class Delivery(models.Model):
	STATUS_CHOICES = (
		('wd', 'Waiting to be dispatched'),
		('cbd', 'Canceled before dispatch'),
		('rd', 'Rejected by dispatcher'),
		('wp', 'Waiting pick up'),
		('cbp', 'Canceled before pick up'),
		('ap', 'About pickup'),
		('cop', 'Canceled on pickup'),
		('pf', 'Pick up failure'),
		('pr', 'Partially reject pickup'),
		('rp', 'Reject pickup'),
		('pp', 'Partially picked up '),
		('p', 'Picked up '),
		('cbh', 'Canceled before handover'),
		('ah', 'About handover'),
		('coh', 'Canceled on handover'),
		('hf', 'Handover failure'),
		('pd', 'Partially Delivered'),
		('d', 'Delivered'), # Job is done
	)
	PAYMENT_TYPES = (
		('po', 'Payed Online'), # payed using online gateways(debit, paypal, strip, ...)
		('pd', 'Payed from Deposit'), # payed from user's deposit
		('os', 'On site payment'), # Not payed, will be payed when giving package to courier
	)
	user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
	request_time_created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
	request_time_last_update = models.DateTimeField(auto_now=True, blank=False, null=False)
	delivery_time = models.DateTimeField(blank=True, null=True)
	from_address = models.ForeignKey('Address', related_name='from_address', on_delete=models.CASCADE,)
	status = models.CharField(_('Status'), max_length=3, default='wd', choices=STATUS_CHOICES)
	cost = models.DecimalField(max_digits=6, decimal_places=2, blank=False, null=False, default=0.0)
	payment_type = models.CharField(_('Payment Types'), max_length=2, default='os', choices=PAYMENT_TYPES)
	payment = models.OneToOneField(Payment, on_delete=models.CASCADE, blank=True, null=True)
	service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE, blank=True, null=True)
	courier = models.ForeignKey(Courier, on_delete=models.SET(-1), blank=True, null=True)
	dispatcher = models.ForeignKey(Dispatcher, on_delete=models.SET(-1), blank=True, null=True)
	comments = models.ManyToManyField('Comment')

	def __str__(self):
		return "Delivery {}({})".format(self.id, self.status)

	def get_unhandled_packages(self):
		return Package.objects.filter(delivery=self, status='ap')

	def get_picked_packages(self):
		return Package.objects.filter(delivery=self, status='p')

	def get_rejected_packages(self):
		return Package.objects.filter(delivery=self, status='rp')

	def is_multi_package(self):
		package_count = self.package_set.all().count()
		if package_count > 1:
			return True
		else:
			return False

	def set_package_status(self, package_status, actor):
		packages = Package.objects.filter(delivery=self)
		for package in packages:
			if package.is_mutable(actor):
				package.status = package_status
				package.save()
				print("Heloooooooooo " + package.status )
			else:
				print("Package.status[id=" + str(package.id) + "]: " + package.status + " is not mutable")

	def get_proper_status(self):
		packages = Package.objects.filter(delivery=self)
		status_list = []
		for package in packages:
			status_list.append(package.status)
		unique_status_list = list(set(status_list))
		if len(unique_status_list) > 1:
			if "wd" in unique_status_list:
				return "wd"
			elif "wp" in unique_status_list:
				return "wp"
			elif "d" in unique_status_list:
				return "pd"
			elif "p" in unique_status_list:
				return "pp"
			elif "ap" in unique_status_list:
				return "ap"
			elif "rp" in unique_status_list:
				return "pr"
			elif "hf" in unique_status_list:
				return "hf"
			elif "coh" in unique_status_list:
				return "coh"
			elif "cbh" in unique_status_list:
				return "cbh"
			elif "cop" in unique_status_list:
				return "cop"
			elif "cbp" in unique_status_list:
				return "cbp"
			elif "cbd" in unique_status_list:
				return "cbd"
		elif len(unique_status_list) == 1 :
			return unique_status_list[0]

	def set_status_by_action(self, action, actor):
		if action == "cancel_before_dispatch":
			self.status = "cbd"
			self.set_package_status("cbd", actor)
		elif action == "reject_delivery":
			self.status = "rd"
			self.set_package_status("rd", actor)
		elif action == "dispatch":
			self.status = "wp"
			self.set_package_status("wp", actor)
		elif action == "auto_dispatch":
			self.status = "wp"
			self.set_package_status("wp", 'auto_dispatch')
		elif action == "cancel_before_pickup":
			self.status = "cbp"
			self.set_package_status("cbp", actor)
		elif action == "add_to_pickup_target":
			self.status = "ap"
			self.set_package_status("ap", actor)
		elif action == "undo_add_to_pickup_target":
			packages = self.package_set.all()
			for package in packages:
				if package.status == "rp":
					comments = Comment.objects.filter(package=package)
					for comment in comments:
						if comment.for_reject:
							comment.delete()
			self.status = "wp"
			self.set_package_status("wp", actor)
		elif action == "done_with_pickup":
			self.status = self.get_proper_status()
		elif action == "report_pickup_failure":
			self.status = "pf"
			self.set_package_status("pf", actor)



	def get_user_proper_name(self):
		if self.user.get_full_name():
			return self.user.get_full_name()
		else:
			return self.user.username

	def available_options_for_user(self):
		option = []
		if self.status == "wd":
			option.append('cancel_before_dispatch')
			option.append('cancel request')
		elif self.status == "wp":
			option.append('cancel_before_pickup')
			option.append("cancel request")
		return option

	def has_mutable_package(self):
		packages = self.package_set.all()
		for package in packages:
			if package.is_mutable("user"):
				return True
		return False

	def get_packages_to_pickup(self):
		packages = self.package_set.filter(status='wp')
		return packages

	def get_packages_in_pickup_target(self):
		packages = self.package_set.filter(status__in=Package.mutable_status_list['courier'])

		return packages


class PackageTemplate(models.Model):
	SIZE_TYPES = (
		('t', 'Use size fields in this template'),
		('m', 'Measured by Courier'),
		('c', 'Custom Size'),
	)
	title = models.CharField(_('Package Name'), max_length=120, blank=True, null=True)
	description = models.TextField(_('Comment'), max_length=120, blank=True, null=True)
	size_type = models.CharField(_('Measurment Types'), max_length=1, default='t', choices=SIZE_TYPES)
	# TODO set blank and null to False
	weight = models.CharField(_('Package Weight'), max_length=120, blank=True, null=True)
	weight_metrics = models.CharField(_('Weight Standard'), max_length=2, default='kg', choices=WEIGHT_METRICS)
	height = models.CharField(_('Package Size'), max_length=120, blank=True, null=True)
	width = models.CharField(_('Package Size'), max_length=120, blank=True, null=True)
	length = models.CharField(_('Package Sie'), max_length=120, blank=True, null=True)

	def __str__(self):

		return self.title


class Package(models.Model):
	STATUS_CHOICES = (
		('wd', 'Waiting for dispatcher'),  # initial state
		('cbd', 'Canceled before dispatch'),
		('rd', 'Reject delivery'),
		('wp', 'Waiting to pick up'),
		('cbp', 'Canceled before pick up'),
		('ap', 'About pick up'),
		('cop', 'Canceled on pickup'),
		('pf', 'Pickup failure'),
		('rp', 'Rejected pick up'),
		('p', 'Picked up'),
		('cbh', 'Canceled before handover'),
		('ah', 'About handover'),
		('coh', 'Canceled on handover'),
		('hf', 'Handover failure'),
		('d', 'Delivered'),
	)
	tracking_id = models.CharField(_('Tracking Code'), max_length=120, blank=True, null=True)
	delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE)
	name = models.CharField(_('Package Name'), default="Package", max_length=120, blank=True, null=True)
	contact = models.CharField(_('Contact\'s name'), max_length=120, blank=True, null=True)
	to_address = models.ForeignKey('Address', related_name='to_address', on_delete=models.CASCADE,)
	description = models.CharField(_('Description'), max_length=100, blank=True, null=True )
	template = models.ForeignKey(PackageTemplate, on_delete=models.CASCADE, blank=True, null=True)
	status = models.CharField(_('Status'), max_length=3, default='wd', choices=STATUS_CHOICES)
	weight = models.CharField(_('Package Weight'), max_length=120, blank=True, null=True)
	weight_metrics = models.CharField(_('Weight Standard'), max_length=2, default='kg', choices=WEIGHT_METRICS)
	height = models.CharField(_('Package height'), max_length=120, blank=True, null=True)
	width = models.CharField(_('Package width'), max_length=120, blank=True, null=True)
	length = models.CharField(_('Package length'), max_length=120, blank=True, null=True)
	comments = models.ManyToManyField('Comment')
	signature = models.BooleanField(default=False)
	tracking_code_sharing_sms = models.BooleanField(default=False)
	tracking_code_sharing_email = models.BooleanField(default=False)
	signer_name = models.CharField(_('Signer Name'), max_length=120, blank=True, null=True)
	signer_phone = models.CharField(_('Signer Phone'), max_length=15, blank=True, null=True)
	pickup_time = models.DateTimeField(blank=True, null=True)
	handover_time = models.DateTimeField(blank=True, null=True)
	mutable_status_list = {
		'user': ['wd', 'wp', 'ap', 'p', 'ah'],
		'dispatcher': ['wd'],
		'auto_dispatch': ['wd'],
		'courier': ['wd', 'wp', 'rp', 'pf', 'ap', 'p', 'hf', 'ah']
	}

	def __str__(self):
		return self.name

	def set_status_by_action(self, action):
		update_delivery_status = True
		if action == "cancel_before_dispatch":
			self.status = "cbd"
		if action == "cancel_before_pickup":
			self.status = "cbp"
		elif action == "cancel_on_pickup":
			self.status = "cop"
		elif action == "reject_pickup":
			self.status = "rp"
			update_delivery_status = False
		elif action == "undo_reject_pickup":
			self.status = "ap"
			update_delivery_status = False
		elif action == "pickup_rejected":
			self.status = "p"
			comments = Comment.objects.filter(package=self)
			for comment in comments:
				if comment.for_reject:
					comment.delete()
		elif action == "pickup":
			self.status = "p"
			self.pickup_time = datetime.now()
			update_delivery_status = False
		elif action == "undo_pickup":
			self.status = "ap"
			self.pickup_time = None
			update_delivery_status = False
		elif action == "cancel_before_handover":
			self.status = "cbh"
		elif action == "add_to_handover_target":
			self.status = "ah"
		elif action == "undo_add_to_handover_task":
			self.status = "p"
		elif action == "cancel_on_handover":
			self.status = "coh"
		elif action == "report_handover_failure":
			self.status = "hf"
		elif action == "handover":
			self.status = "d"
		self.save()
		delivery = self.delivery
		if delivery.is_multi_package() and update_delivery_status:
			delivery.status = delivery.get_proper_status()
			delivery.save()
		elif update_delivery_status:
			delivery.status = self.status
			delivery.save()

	def is_mutable(self, actor="user"):
		if self.status in self.mutable_status_list[actor]:
			return True
		else:
			return False

	def available_option_for_user(self):
		option = []
		if self.status == "wd":
			option.append('cancel_before_dispatch')
			option.append('cancel')
		if self.status == self.status == "wp":
			option.append('cancel_before_pickup')
			option.append('cancel')
		elif self.status == "ap":
			option.append('cancel_on_pickup')
			option.append('cancel')
		elif self.status == "p":
			option.append('cancel_before_handover')
			option.append('cancel')
		elif self.status == "ah":
			option.append('cancel_on_handover')
			option.append('cancel')

		return option

	def check_user(self,user):
		package_user = self.delivery.user
		if user == package_user:
			return True
		else:
			print("user mismatch")
			return False

	def save(self, *args, **kwargs):
		from django.contrib.sites.models import Site
		from settings.models import SiteSettings
		current_site = Site.objects.get_current()
		site_settings = SiteSettings.objects.get(site=current_site)
		if not self.tracking_id:
			import random
			while True:
				random_id = random.randint(10000000, 99999999)  # 8 digit random number
				prefix = site_settings.tracking_id_prefix if site_settings.tracking_id_prefix else ""
				suffix = site_settings.tracking_id_suffix if site_settings.tracking_id_suffix else ""
				tracking_id = "{}{}{}".format(prefix, random_id, suffix)
				try:
					package = Package.objects.get(tracking_id=tracking_id)
				except Package.DoesNotExist:
					break
			self.tracking_id = tracking_id
		super(Package, self).save(*args, **kwargs)


class Country(models.Model):
	name = models.CharField(_('Country'), max_length=100, blank=False, null=False)

	def __str__(self):
		return self.name


class Province(models.Model):
	name = models.CharField(_('Province'), max_length=100, blank=False, null=False)
	country = models.ForeignKey(Country, on_delete=models.CASCADE, blank=False, null=False)

	def __str__(self):
		return "{} | {}".format(self.name.capitalize(), self.country.name.capitalize())


class City(models.Model):
	name = models.CharField(_('City'), max_length=100, blank=False, null=False)
	province = models.ForeignKey(Province, on_delete=models.CASCADE, blank=False, null=False)

	def __str__(self):
		return self.name


class Address(models.Model):
	CATEGORY = (
		('pa', 'pick up address'),
		('da', 'destination address')
	)
	user = models.ForeignKey(User, on_delete=models.CASCADE )
	title = models.CharField(_('Title'), max_length=256, blank=True, null=True)
	category = models.CharField(_('Category'), max_length=2, default='da', choices=CATEGORY)
	city = models.ForeignKey(City, on_delete=models.CASCADE, default=1)
	zip = models.CharField(_('ZIP'), max_length=32, blank=False, null=False)
	address1 = models.TextField(_('Address 1'), max_length=256, blank=False, null=False)
	address2 = models.TextField(_('Address 2'), max_length=256, blank=True, null=True)
	phone = models.CharField(_('Phone'), max_length=12, blank=False, null=False)
	fax = models.CharField(_('Fax'), max_length=12, blank=True, null=True)
	email = models.EmailField(_('E-Mail'), max_length=100, blank=True, null=True)
	hash = models.CharField(_('Hash Address'), max_length=32, blank=False, null=False)
	archived = models.BooleanField(default=False)

	class Meta:
		unique_together = (
			('user', 'title'),
			('user', 'hash')
		)

	def short(self):
		zone_system = ZoneSystem.objects.all().first()
		if zone_system.name == "p":
			zs = "P.C"
		elif zone_system == "z":
			zs = "ZIP"
		if self.address2:
			return "{}, {}. {}: {}".format(self.address2, self.address1, zs, self.zip)
		else:
			return "{}. {}: {}".format(self.address1, zs, self.zip)

	def get_one_line(self):
		return "{}, {}, {}, {}, {}, {}".format(self.address2, self.address1, self.city.name.capitalize(),
			self.get_province().name.capitalize(), self.get_country().name.capitalize(), self.get_zone_system())

	def get_one_line_hash(self):
		one_line = "{}, {}, {}, {}".format(self.get_one_line(), self.phone, self.fax, self.email)
		from hashlib import md5
		return md5(one_line.encode('utf-8')).hexdigest()

	def __str__(self):
		return self.get_one_line()

	def get_province(self):
		province = Province.objects.get(city=self.city)
		return province

	def get_country(self):
		country = Country.objects.get(province=self.get_province())
		return country

	def get_zone_system(self):
		zone_system = ZoneSystem.objects.all().first()
		if zone_system:
			return "{}:{}".format(zone_system.get_name_display(), self.zip)
		else:
			return "Zip:{}".format(self.zip)

	def is_referenced(self):
		deliveries = Delivery.objects.filter(from_address=self)
		if deliveries.count() > 0:
			return True
		else:
			packages = Package.objects.filter(to_address=self)
			if packages.count() > 0:
				return True
			else:
				return False

	def save(self, *args, **kwargs):
		if self.title: self.title = self.title.lower()
		if self.zip: self.zip = self.zip.strip()
		if self.address1: self.address1 = self.address1.strip()
		if self.address2: self.address2 = self.address2.strip()
		if self.phone: self.phone = self.phone.strip()
		if self.fax: self.fax = self.fax.strip()
		if self.email: self.email = self.email.strip()

		self.hash = self.get_one_line_hash()
		super(Address, self).save(*args, **kwargs)


class Comment(models.Model):
	USER_TYPE = (
		('v', 'Visitor'),
		('u', 'User'),
		('d', 'dispatcher'),
		('c', 'Courier'),
	)
	REASON = (
		('pr', 'Pickup Rejection'),
		('dr', 'Delivery Rejection'),
		('pf', 'Pick up Failure'),
		('hf', 'Handover Failure'),
		('mi', 'More information'),
	)
	user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
	actor = models.CharField(_('Actor'), max_length=1, choices=USER_TYPE)
	for_reject = models.BooleanField(default=False)
	reason = models.CharField(_('Reason'), max_length=2, default="", choices=REASON)
	message = models.CharField(_('Message'), max_length=100, blank=False, null=False )
	time = models.DateTimeField(auto_now_add=True, blank=True, null=True)

	def set_actor(self, request):
		if request.user.is_authenticated:
			if request.user.is_courier:
				self.actor = 'c'
			elif request.user.is_dispatcher:
				self.actor = 'd'
			else:
				self.actor = 'u'
		else:
			self.actor = 'v'


class SingletonModel(models.Model):
	class Meta:
		abstract = True

	def save(self, *args, **kwargs):
		self.pk = 1
		super(SingletonModel, self).save(*args, **kwargs)

	def delete(self, *args, **kwargs):
		pass

	@classmethod
	def load(cls):
		obj, created = cls.objects.get_or_create(pk=1)
		return obj


class ControlPanel(SingletonModel):
	auto_dispatch = models.BooleanField(default=False)
	auto_dispatch_courier = models.ForeignKey(Courier, on_delete=models.SET_NULL, blank=True, null=True)
	new_task_for_dispatcher = models.BooleanField(default=False)
	new_task_for_courier = models.CharField(max_length=20, blank=True, default=",", null=False)

	def set_auto_dispatch(self, courier_id):
		try:
			courier = Courier.objects.get(id=courier_id)
			self.auto_dispatch = True
			self.auto_dispatch_courier = courier
			self.save()
			return True
		except Courier.DoesNotExist:
			return False

	def unset_auto_dispatch(self):
		self.auto_dispatch = False
		self.auto_dispatch_courier = None
		self.save()

	def is_auto_dispatch(self):
		return self.auto_dispatch

	def set_new_task_for_dispatcher(self):
		self.new_task_for_dispatcher = True
		self.save()

	def unset_new_task_for_dispatcher(self):
		self.new_task_for_dispatcher = False
		self.save()

	def has_dispatcher_new_task(self):
		return self.new_task_for_dispatcher

	def set_new_task_for_courier(self, courier_id):
		try:
			courier = Courier.objects.get(id=courier_id)
			if self.new_task_for_courier is None or self.new_task_for_courier == "":
				self.new_task_for_courier = "," + str(courier_id)
				self.save()
			elif not self.has_courier_new_task(courier_id):
				self.new_task_for_courier += "," + str(courier_id)
				self.save()
			else:
				pass
		except Courier.DoesNotExist:
			pass

	def unset_new_task_for_courier(self, courier_id):
		courier_id = str(courier_id)
		if self.new_task_for_courier is not None:
			if str(self.new_task_for_courier).strip() != "":
				id_list = self.new_task_for_courier.split(',')
				if courier_id in id_list:
					id_list.remove(courier_id)
				self.new_task_for_courier = ','.join(id_list)
				self.save()

	def has_courier_new_task(self, courier_id):
		if self.new_task_for_courier is not None:
			if str(self.new_task_for_courier).strip() != "":
				courier_id = str(courier_id)
				id_list = str(self.new_task_for_courier).split(',')
				if courier_id in id_list:
					return True
				else:
					return False
			else:
				return False
		else:
			print("location 9")
			return False
