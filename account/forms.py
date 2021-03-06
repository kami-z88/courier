from __future__ import unicode_literals
from django.utils.safestring import mark_safe
from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from .models import AccountSignup, Profile
from .settings import REMEMBER_ME_DAYS


USERNAME_RE = r'^[\.\w]+$'
attrs_dict = {'class': 'required'}


class SignupForm(forms.Form):
	"""
	Form for creating a new user account.
	Username must contain only letters, numbers, dots and underscores.
	"""
	username = forms.RegexField(regex=USERNAME_RE, max_length=128, widget=forms.TextInput(attrs=attrs_dict), label=_("Username"),
								error_messages={'invalid': _('Username must contain only letters, numbers, dots and underscores.')})
	email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': _("Email"), 'class': 'required'}), label=_("Email"))
	password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False), label=_("Password"))
	password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False), label=_("Repeat password"))
	tos = forms.BooleanField(widget=forms.CheckboxInput(attrs=attrs_dict),
							 label=mark_safe(_('I have read and agree to the <a href="#" >Terms of Service<a>')),
							 error_messages={'required': _('You must agree to the terms to register.')})

	def clean_username(self):
		"""
		Validate that the username is alphanumeric and is not already in use.
		"""
		try:
			user = get_user_model().objects.get(username__iexact=self.cleaned_data['username'])
		except get_user_model().DoesNotExist:
			pass
		else:
			if AccountSignup.objects.filter(user__username__iexact=self.cleaned_data['username']).exclude(activation_key='active'):
				raise forms.ValidationError(_('This username is already taken but not confirmed. Please check your email for verification steps.'))
			raise forms.ValidationError(_('This username is already taken.'))
		return self.cleaned_data['username']

	def clean_email(self):
		""" Validate that the e-mail address is unique. """
		if get_user_model().objects.filter(email__iexact=self.cleaned_data['email']):
			if AccountSignup.objects.filter(user__email__iexact=self.cleaned_data['email']).exclude(activation_key='active'):
				raise forms.ValidationError(_('This email is already in use but not confirmed. Please check your email for verification steps.'))
			raise forms.ValidationError(_('This email is already in use. Please supply a different email.'))
		return self.cleaned_data['email']

	def clean(self):
		"""
		Validates that the values entered into the two password fields match.
		"""
		if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
			if self.cleaned_data['password1'] != self.cleaned_data['password2']:
				raise forms.ValidationError(_('The two password fields didn\'t match.'))
		return self.cleaned_data

	def save(self):
		"""
		Creates a new user and account. Returns the newly created user.
		"""
		username, email, password = (self.cleaned_data['username'],
									 self.cleaned_data['email'],
									 self.cleaned_data['password1'])
		new_user = AccountSignup.objects.create_user(username, email, password,)
		return new_user


class SinginForm(forms.Form):
	"""
	A custom form where the identification can be a e-mail address or username.
	"""
	identification = forms.CharField(label=_("Email or Username"),
									widget=forms.TextInput(attrs=attrs_dict),
									max_length=75,
									error_messages={'required': _("Either supply us with your email or username.")})
	password = forms.CharField(label=_("Password"),
								widget=forms.PasswordInput(attrs=attrs_dict, render_value=False))
	remember_me = forms.BooleanField(widget=forms.CheckboxInput(),
									required=False,
									label=_('Remember me for %(days)d days') % {'days': REMEMBER_ME_DAYS})

	def clean(self):
		"""
		Checks for the identification and password.
		If the combination can't be found will raise an invalid sign in error.
		"""
		identification = self.cleaned_data.get('identification')
		password = self.cleaned_data.get('password')

		if identification and password:
			user = authenticate(username=identification, password=password)
			if user is None:
				raise forms.ValidationError(_("Please enter a correct username or email and password. Note that both fields are case-sensitive."))
		return self.cleaned_data


class EditAccountForm(forms.ModelForm):
	"""
	Form for editing user profiles
	"""

	def __init__(self, *args, **kw):
		super(EditAccountForm, self).__init__(*args, **kw)
		self.fields['password'].widget = forms.PasswordInput()
		self.fields['password'].required = False

		self.fields['username'].widget.attrs = {'before_addon': _("fas fa-user"),}
		self.fields['email'].widget.attrs = {'before_addon': _("fas fa-envelope-o"),}
		self.fields['first_name'].widget.attrs = {'before_addon': _("fas fa-user-o"),}
		self.fields['last_name'].widget.attrs = {'before_addon': _("fas fa-user-o"),}
		self.fields['password'].widget.attrs = {'before_addon': _("fas fa-eye-slash "),}

		self.fields.keyOrder = [
			'username',
			'email',
			'first_name',
			'last_name',
			'password',
			]

	class Meta:
		model = User
		fields = ('username', 'email', 'first_name', 'last_name', 'password')

	def clean_username(self):
		username = self.cleaned_data.get('username')
		try:
			user = User.objects.get(username=username)
			if user.pk == self.instance.id:
				return username
		except User.DoesNotExist:
			return username
		raise forms.ValidationError("This user already exist. choose another username!")

	def clean_email(self):
		email = self.cleaned_data.get('email')
		try:
			user = User.objects.get(email=email)
			if user.pk == self.instance.id:
				return email
		except User.DoesNotExist:
			return email
		raise forms.ValidationError('This email address is already in use. Please supply a different email address.')

	def clean_password(self):
		password = self.cleaned_data.get('password')
		if 8 > len(password) > 0:
			raise forms.ValidationError('This Password is too short. it must be at least 8 characters.')
		else:
			return password

	def save(self, commit=True):
		# Ignore Password field in this form
		EditAccountForm.Meta.fields = tuple(x for x in EditAccountForm.Meta.fields if x != 'password')
		user = super(EditAccountForm, self).save(commit=False)
		user.username = self.cleaned_data['username']
		user.email = self.cleaned_data['email']
		if self.cleaned_data['password'] and len(self.cleaned_data['password'])>8:
			user.set_password(self.cleaned_data['password'])
		if commit:
			user.save()
		return user


class EditProfileForm(forms.ModelForm):
	class Meta:
		model = Profile
		fields = ('email',)


class UploadPhotoForm(forms.ModelForm):
	class Meta:
		model = Profile
		fields = ('photo',)


class EditUserForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ('first_name', 'last_name')
