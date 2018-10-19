from django.db import models
from django.contrib.auth.models import User, AnonymousUser
from django.utils import timezone, translation, six
from django.utils.translation import ugettext_lazy as _
import os

WEIGHT_METRICS = (
	('kg', 'Kilogram'),
	('lb', 'Pounds'),
)


# used to get dynamic directory based on user's id
def get_courier_avatar_photo_path(instance, filename):
	name, ext = os.path.splitext(filename)
	filename = 'avatar{}'.format(ext)
	return "courier_avatar/{0}".format(filename)

def get_dispatcher_avatar_photo_path(instance, filename):
	name, ext = os.path.splitext(filename)
	filename = 'avatar{}'.format(ext)
	return "courier_avatar/{0}".format(filename)

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
	avatar = models.ImageField(_('If you chose "Upload Image" as avatar option this image will be used.'),
							   upload_to=get_dispatcher_avatar_photo_path, blank=True, null=True)


class Courier(models.Model):
	user = models.OneToOneField(User, related_name='courier', on_delete=models.CASCADE)
	avatar = models.ImageField(_('If you chose "Upload Image" as avatar option this image will be used.'),
							   upload_to=get_courier_avatar_photo_path, blank=True, null=True)


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
		('wd', 'Waiting to be dispatched'), # Dispatcher has not dispatched to any courier
		('rd', 'Rejected by dispatcher'), # Dispatcher has rejected delivery request
		('wc', 'Waiting for courier'), # Dispatcher has chosen the courier for this delivery
		('ap', 'About pickup'), # Courier is on the way to pickup this delivery
		('rc', 'Rejected by courier'), # Courier has rejected the job
		('pp', 'Partially picked up '), # Courier has picked up some of  package(s) and rejected others
		('pc', 'Picked up by courier'), # Courier has picked up all package(s)
		('ca', 'Can\'t be accomplished'), # Courier can't do the delivery for the reason mentioned
		('c', 'Canceled by requester'), # Requester of delivery has canceled the order before submission
		('pd', 'Partially Delivered'), # Delivery of some packages has completed but not all of them
		('d', 'Delivered'), # Job is done
	)
	PAYMENT_TYPES = (
		('po', 'Payed Online'), # payed using online gateways(debit, paypal, strip, ...)
		('pd', 'Payed from Deposit'), # payed from user's deposit
		('os', 'On site payment'), # Not payed, will be payed when giving package to courier
	)
	user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
	tracking_id = models.CharField(_('Tracking Code'), max_length=120, blank=True, null=True)
	request_time_created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
	request_time_last_update = models.DateTimeField(auto_now=True, blank=False, null=False)
	delivery_time = models.DateTimeField(blank=True, null=True)
	from_address = models.ForeignKey('Address', related_name='from_address', on_delete=models.CASCADE,)
	status = models.CharField(_('Status'), max_length=2, default='wd', choices=STATUS_CHOICES)
	cost = models.DecimalField(max_digits=6, decimal_places=2, blank=False, null=False, default=0.0)
	payment_type = models.CharField(_('Payment Types'), max_length=2, default='os', choices=PAYMENT_TYPES)
	payment = models.OneToOneField(Payment, on_delete=models.CASCADE, blank=True, null=True)
	service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE, blank=True, null=True)
	courier = models.ForeignKey(Courier, on_delete=models.SET(-1), blank=True, null=True)
	dispatcher = models.ForeignKey(Dispatcher, on_delete=models.SET(-1), blank=True, null=True)
	comments = models.ManyToManyField('Comment')

	def __str__(self):
		return "Delivery {}({})".format(self.id, self.status)

	def save(self, *args, **kwargs):
		import random
		from django.contrib.sites.models import Site
		from settings.models import SiteSettings

		current_site = Site.objects.get_current()
		site_settings = SiteSettings.objects.get(site=current_site)
		while(True):
			random_id = random.randint(10000000, 99999999)  # 8 digit random number
			prefix = site_settings.tracking_id_prefix if site_settings.tracking_id_prefix else ""
			suffix = site_settings.tracking_id_suffix if site_settings.tracking_id_suffix else ""
			tracking_id = "{}{}{}".format(prefix, random_id, suffix)
			try:
				delivery = Delivery.objects.get(tracking_id=tracking_id)
			except:
				break

		self.tracking_id = tracking_id
		super(Delivery, self).save(*args, **kwargs)

	def get_user_proper_name(self):
		if self.user.get_full_name():
			return self.user.get_full_name()
		else:
			return self.user.username

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
		('wp', 'Waiting to pickup'), # Courier has not picked up the packages yet
		('rc', 'Rejected by courier'), # Courier has rejected delivering this package for mentioned reason
		('pc', 'Picked up by courier'), # Courier has picked up the package(s)
		('ah', 'About handover'), # Courier has picked up the package(s)
		('ca', 'Can\'t be accomplished'), # Courier can't hand over the package for the reason mentioned
		('c', 'Canceled by requester'), # Requester of delivery has canceled the order before submission
		('d', 'Delivered'), # Job is done
	)
	tracking_id = models.CharField(_('Tracking Code'), max_length=120, blank=True, null=True)
	delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE)
	name = models.CharField(_('Package Name'), default="Package", max_length=120, blank=True, null=True)
	contact = models.CharField(_('Contact\'s name'), max_length=120, blank=True, null=True)
	to_address = models.ForeignKey('Address', related_name='to_address', on_delete=models.CASCADE,)
	template = models.ForeignKey(PackageTemplate, on_delete=models.CASCADE, blank=True, null=True)
	status = models.CharField(_('Status'), max_length=2, default='wp', choices=STATUS_CHOICES)
	weight = models.CharField(_('Package Weight'), max_length=120, blank=True, null=True)
	weight_metrics = models.CharField(_('Weight Standard'), max_length=2, default='kg', choices=WEIGHT_METRICS)
	height = models.CharField(_('Package height'), max_length=120, blank=True, null=True)
	width = models.CharField(_('Package width'), max_length=120, blank=True, null=True)
	length = models.CharField(_('Package length'), max_length=120, blank=True, null=True)
	comments = models.ManyToManyField('Comment')
	signature = models.BooleanField(default=False)
	signer_name = models.CharField(_('Signer Name'), max_length=120, blank=True, null=True)
	signer_phone = models.CharField(_('Signer Phone'), max_length=15, blank=True, null=True)
	pickup_time = models.DateTimeField(blank=True, null=True)
	handover_time = models.DateTimeField(blank=True, null=True)

	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		import random
		from django.contrib.sites.models import Site
		from settings.models import SiteSettings

		current_site = Site.objects.get_current()
		site_settings = SiteSettings.objects.get(site=current_site)
		while(True):
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


class Address(models.Model):
	state = models.CharField(_('State'), max_length=256, blank=True, null=True)
	city = models.CharField(_('City'), max_length=256, blank=True, null=True)
	zip = models.CharField(_('ZIP'), max_length=32, blank=False, null=False)
	address1 = models.TextField(_('Address 1'), max_length=256, blank=False, null=False)
	address2 = models.TextField(_('Address 2'), max_length=256, blank=True, null=True)
	phone = models.CharField(_('Phone'), max_length=12, blank=False, null=False)
	fax = models.CharField(_('Fax'), max_length=12, blank=True, null=True)
	email = models.EmailField(_('E-Mail'), max_length=100, blank=True, null=True)
	hash = models.CharField(_('Hash Address'), max_length=32, blank=True, null=True)

	def get_one_line(self):
		return "{}, {}, {}, {}, {}, Phone:{}, Fax:{}".format(self.address2, self.address1, self.city, self.state, self.zip, self.phone, self.fax)

	def get_one_line_hash(self):
		one_line = "{}, {}, {}, {}, {}, {}, {}, {}".format(self.phone, self.fax, self.email, self.address2, self.address1, self.city, self.state, self.zip)
		from hashlib import md5
		return md5(one_line.encode('utf-8')).hexdigest()

	def __str__(self):
		return self.get_one_line()

	def save(self, *args, **kwargs):
		if self.state: self.state = self.state.strip()
		if self.city: self.city = self.city.strip()
		if self.zip: self.zip = self.zip.strip()
		if self.address1: self.address1 = self.address1.strip()
		if self.address2: self.address2 = self.address2.strip()
		if self.phone: self.phone = self.phone.strip()
		if self.fax: self.fax = self.fax.strip()
		if self.email: self.email = self.email.strip()

		self.hash = self.get_one_line_hash()
		super(Address, self).save(*args, **kwargs)


class AddressBook(models.Model):
	USED_FOR = (
		('s', 'source address'),
		('d', 'destination address')
	)
	user = models.ForeignKey(User, on_delete=models.CASCADE )
	address = models.ForeignKey(Address, on_delete=models.CASCADE)
	title = models.CharField(_('Title'), max_length=256, blank=True, null=True)
	used_for = models.CharField(_('Used For'), max_length=1, default='s', choices=USED_FOR)

	def __str__(self):
		if self.user.get_full_name():
			name = self.user.get_full_name()
		else:
			name = "@{}".format(self.user.username)
		return "{}: {}".format( name, self.address.get_one_line() )


class Comment(models.Model):
	USER_TYPE = (
		('v', 'Visitor'),
		('u', 'User'),
		('d', 'dispatcher'),
		('c', 'Courier'),
	)
	user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
	actor = models.CharField(_('Actor'), max_length=1, choices=USER_TYPE)
	for_reject = models.BooleanField(default=False)
	message = models.CharField(_('Message'), max_length=100, blank=False, null=False )
	time = models.DateTimeField(auto_now_add=True, blank=True, null=True)
