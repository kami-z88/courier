"""
This model is used to handle registration related features such as email confirmation
"""
import datetime, os
import random
import string
from django.conf import settings
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.db import models
from django.contrib.auth.models import User, AnonymousUser
from django.db.models.signals import post_save
from django.utils import timezone, translation, six
from django.utils.translation import ugettext_lazy as _
from sorl.thumbnail import get_thumbnail, ImageField, delete
from .modules.functions import generate_sha1


import account.settings as profile_settings
from .modules.language_country import COUNTRIES, LANGUAGES
from .modules.mail import send_mail
from .managers import AccountManager
from .utils import get_grphoto


# random string generator
def string_generator(size):
    chars = string.ascii_uppercase + string.ascii_lowercase
    return ''.join(random.choice(chars) for _ in range(size))


# used to get dynamic directory based on user's id
def set_photo_file_path(instance, filename):
	name, ext = os.path.splitext(filename)
	filename = 'photo_{}{}'.format(string_generator(4), ext)
	salt, hash = generate_sha1(instance.user.username, instance.user.pk)
	return "photo/{0}{1}/{2}".format(hash, salt, filename)


class AccountSignup(models.Model):
	user = models.OneToOneField('auth.user', verbose_name=_('user'), on_delete=models.CASCADE,)
	last_active = models.DateTimeField(_('last active'), blank=True, null=True)
	activation_key = models.CharField(_('activation key'), max_length=40, blank=True)
	activation_notification_send = models.BooleanField(_('notification send'), default=False)
	email_unconfirmed = models.EmailField(_('unconfirmed email address'), blank=True)
	email_confirmation_key = models.CharField(_('unconfirmed email verification key'), max_length=40, blank=True)
	email_confirmation_key_created = models.DateTimeField(_('creation date of email confirmation key'), blank=True, null=True)
	objects = AccountManager()

	class Meta:
		verbose_name = _('registration')
		verbose_name_plural = _('registrations')

	def __str__(self):
		return '%s' % self.user.username

	def change_email(self, email):
		"""
		Changes the email address for a user.
		A user needs to verify this new email address before it becomes
		active. By storing the new email address in a temporary field --
		``temporary_email`` -- we are able to set this email address after the
		user has verified it by clicking on the verification URI in the email.
		This email gets send out by ``send_verification_email``.
		
		:param email: The new email address that the user wants to use.
		"""
		from .modules.functions import generate_sha1
		self.email_unconfirmed = email
		salt, hash = generate_sha1(self.user.username)
		self.email_confirmation_key = hash
		self.email_confirmation_key_created = timezone.now()
		self.save()
		# Send email for activation
		self.send_confirmation_email()

	def send_confirmation_email(self):
		"""
		Sends an email to confirm the new email address.
		"""
		context = {'user': self.user,
					'new_email': self.email_unconfirmed,
					'protocol': settings.DEFAULT_PROTOCOL,
					'confirmation_key': self.email_confirmation_key,
					'site': Site.objects.get_current()}

		mailer = ConfirmationMail(context=context)
		mailer.generate_mail("confirmation", "_old")

		if self.user.email:
			mailer.send_mail(self.user.email)

		mailer.generate_mail("confirmation", "_new")
		mailer.send_mail(self.email_unconfirmed)

	def activation_key_expired(self):
		"""
		Checks if activation key is expired.
		Returns ``True`` when the ``activation_key`` of the user is expired and
		``False`` if the key is still valid.
		"""
		expiration_days = datetime.timedelta(profile_settings.ACTIVATION_DAYS)
		expiration_date = self.user.date_joined + expiration_days
		if self.activation_key == profile_settings.ACTIVATED_TEXT:
			return True
		if timezone.now() >= expiration_date:
			return True
		return False

	def send_activation_email(self):
		"""
		Sends a activation email to the user.
		This email is send when the user wants to activate their newly created
		user.
		"""
		context = {'user': self.user,
					'protocol': settings.DEFAULT_PROTOCOL,
					'activation_days': profile_settings.ACTIVATION_DAYS,
					'activation_key': self.activation_key,
					'site': Site.objects.get_current()}

		mailer = ConfirmationMail(context=context)
		mailer.generate_mail("activation")
		mailer.send_mail(self.user.email)


class ConfirmationMail(object):
	_message_txt = 'emails/{0}_email_message{1}.txt'
	_message_html = 'emails/{0}_email_message{1}.html'
	_subject_txt = 'emails/{0}_email_subject{1}.txt'

	def __init__(self, context):
		self.context = context

	def generate_mail(self, type_mail, version=""):
		self.type_mail = type_mail
		self.message_txt = self._message_txt.format(type_mail, version)
		self.message_html = self._message_html.format(type_mail, version)
		self.subject_txt = self._subject_txt.format(type_mail, version)
		self.subject = self._subject()
		self.message_html = self._message_in_html()
		self.message = self._message_in_txt()

	def send_mail(self, email):
		send_mail(self.subject, self.message,
				  self.message_html, settings.DEFAULT_FROM_EMAIL,
				  [email])

	def _message_in_html(self):
		if settings.EMAIL_FORMAT_HTML:
			return render_to_string(self.message_html, self.context)
		return None

	def _message_in_txt(self):
		if not settings.EMAIL_FORMAT_HTML or not self.message_html:
			return render_to_string(self.message_txt, self.context)
		return None

	def _subject(self):
		subject = render_to_string(self.subject_txt, self.context)
		subject = ''.join(subject.splitlines())
		return subject


class Profile(models.Model):
	TYPE_CHOICES = (
		('n', 'None'),
		('p', 'Person'),
		('c', 'Company'),
	)
	user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
	photo = models.ImageField(upload_to=set_photo_file_path, blank=True, null=True)
	type = models.CharField(_('Gender'), max_length=1, default='n', choices=TYPE_CHOICES)
	email = models.EmailField(blank=True, null=True)
	deposit = models.DecimalField(max_digits=6, decimal_places=2, blank=False, null=False, default=0.0)
	has_photo = True

	def __init__(self, *args, **kwargs):
		super(Profile, self).__init__(*args, **kwargs)
		if not self.photo:
			from .settings import DEFAULT_PHOTO_URL
			self.photo = DEFAULT_PHOTO_URL
			self.has_photo = False

	def get_full_name(self):
		"""
		Returns the full name of the user, or if none is supplied will return the username.
		"""
		user = self.user
		if user.first_name or user.last_name:
			name = "{0} {1}".format(user.first_name, user.last_name)
		else:
			name = user.username
		return name.strip()

	def get_photo_url(self, size=256, crop='center', quality=100):
		"""
		Returns the photo image based on user's settings
		"""
		if self.photo:
			im = get_thumbnail(self.photo, "{0}x{0}".format(size), crop=crop, quality=quality)
			return "{0}files/{1}".format(Site.objects.get_current(), im.name)
		else:
			return profile_settings.DEFAULT_PHOTO_URL

	def delete_photo(self, path=None, unset_path=True):
		from .settings import DEFAULT_PHOTO_URL
		if not path:
			path = self.get_photo_full_path()
		if self.photo and os.path.basename(path) != os.path.basename(DEFAULT_PHOTO_URL):
			os.remove(path)
			delete(self.photo, delete_file=True)
		if unset_path:
			self.photo = None
			self.save()

	def get_photo_full_path(self):
		from project.settings import BASE_DIR
		if self.photo:
			file_path = os.path.join(BASE_DIR, 'project') + self.photo.url
			return file_path

	def __str__(self):
		return self.user.username


def create_profile(sender, **kwargs):
	"""
	Create a user profile for each User
	Set permissions to edit and view profile
	"""
	user = kwargs["instance"]
	if kwargs["created"]:
		user_profile = Profile(user=user)
		user_profile.save()
post_save.connect(create_profile, sender=User)


class AnonymousAccount(object):
	def __init__(self, request=None):
		self.user = AnonymousUser()
		self.timezone = settings.TIME_ZONE
		if request is None:
			self.language = settings.LANGUAGE_CODE
		else:
			self.language = translation.get_language_from_request(request, check_path=True)

	def __str__(self):
		return "AnonymousAccount"
