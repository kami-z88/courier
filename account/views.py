import json
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import update_session_auth_hash
from .forms import SignupForm, SinginForm, EditProfileForm, EditUserForm
from .settings import REMEMBER_ME_DAYS, LOGIN_REDIRECT_URL
from .models import AccountSignup, Profile


def profile(request):
	user = request.user
	user_profile = Profile.objects.get(user=user)
	context = {
		'user': user,
		'profile': user_profile,
	}
	return render(request, "profile.html", context)


def change_password(request):
	data = {}
	if request.method == 'POST':
		user_id = request.POST.get("userId", None)
		pass1 = str(request.POST.get("pass1", None)).strip()
		pass2 = str(request.POST.get("pass2", None)).strip()
		if str(user_id) != str(request.user.id):
			data['error'] = "User ERROR"
		elif len(pass1) < 8:
			data['error'] = "Minimum characters ERROR"
		elif pass1 != pass2:
			data['error'] = "Password and Confirm mismatch"
		else:
			user = request.user
			user_initial_pass = user.password
			user.set_password(pass1)
			user.save()
			update_session_auth_hash(request, user)
			if user_initial_pass != user.password:
				data['result'] = "success"
				request.user = user
			else:
				data['result'] = "failure"
	data = json.dumps(data)
	return HttpResponse(data, content_type='application/json')


def upload_profile_photo(request):
	from .forms import UploadPhotoForm
	profile = Profile.objects.get(user=request.user)
	current_photo_path = profile.get_photo_full_path()
	if request.method == 'POST':
		form = UploadPhotoForm(request.POST, request.FILES, instance=profile)
		if form.is_valid():
			if profile.has_photo:
				profile.delete_photo(current_photo_path, unset_path=False)
			form.save()
	return redirect('profile')


def delete_user_photo(request):
	profile_id = request.GET.get('profileId', None)
	data = {}
	try:
		profile = Profile.objects.get(id=profile_id, user=request.user)
		profile.delete_photo()
	except Profile.DoesNotExist:
		pass
	data = json.dumps(data)
	return HttpResponse(data, content_type='application/json')


def profile_edit(request):
	user = request.user
	user_profile = Profile.objects.get(user=user)
	if request.method == 'POST':
		form_user = EditUserForm(request.POST, instance=user)
		form_profile = EditProfileForm(request.POST, instance=user_profile)
		if form_profile.is_valid() and form_user.is_valid():
			form_user.save()
			updated_profile_instance = form_profile.save(commit=False)
			if not user_profile.has_photo:
				updated_profile_instance.photo = None
			updated_profile_instance.save()
		else:
			print("form is not valid")
	return redirect('profile')


def signup(request):
	"""
	Signup of an account.
	1. Signup with username, email and password
	2. get confirmation email with an activation link
	3. redirect user to homepage or visiting page
	"""
	form = SignupForm()
	if request.method == 'POST':
		form = SignupForm(request.POST, request.FILES)
		if form.is_valid():
			user = form.save()
			if user.id:
				user.is_active = True
				user.photo = None
				user.save()
				login(request, user)
			redirect_url = reverse('profile')
			return redirect(redirect_url)

	context = {
		'form': form,
	}
	return render(request, "signup-form.html", context)


def signin(request):
	"""
	login of an account.
	1. Signin with (username or email) and password
	2. redirect
	"""
	form = SinginForm()
	if request.method == 'POST':
		form = SinginForm(request.POST)
		if form.is_valid():
			identification, password, remember_me = (form.cleaned_data['identification'],
													 form.cleaned_data['password'],
													 form.cleaned_data['remember_me'])
			user = authenticate(username=identification,
								password=password)
			if user.is_active:
				if 'next' in request.GET:
					if request.GET['next']:
						redirect_url = request.GET['next']
					else:
						redirect_url = LOGIN_REDIRECT_URL
				else:
					referer = request.META.get('HTTP_REFERER', '').rstrip('/')
					if referer and not referer.endswith('login'):
						redirect_url = referer
					else:
						redirect_url = '/'
				login(request, user)
				if remember_me:
					request.session.set_expiry(REMEMBER_ME_DAYS * 86400)
				else:
					request.session.set_expiry(0)

				# Whereto now?
				print("checkpoint 1")
				return HttpResponseRedirect(redirect_url)
			else:

				# TODO: add message to show user that he is inactive
				return redirect(LOGIN_REDIRECT_URL)

	context = {
		'form': form,
	}
	return render(request, "signin-form.html", context)


def signout(request, next_page):
	"""
	Signs out the user
	"""
	logout(request)
	request.session.flush()
	referer = request.META.get('HTTP_REFERER', '').rstrip('/')
	if not next_page:
		if referer and not referer.endswith('login'):
			redirect_url = referer
		else:
			redirect_url = '/'
		return HttpResponseRedirect(redirect_url)
	else:
		return HttpResponseRedirect(next_page)


def activate(request, activation_key):
	"""
	Activate a user with an activation key.

	The key is a SHA1 string. When the SHA1 is found with an
	:class:`AccountSignup`, the :class:`User` of that account will be activated.
	After a successful activation the view will redirect to ``success_url``.
	If the SHA1 is not found, the user will be shown the ``failed_url`` template displaying a fail message.
	If the SHA1 is found but expired, ``retry_template`` is used instead so user can get a new activation key.
	"""
	try:
		if not AccountSignup.objects.check_expired_activation(activation_key):
			user = AccountSignup.objects.activate_user(activation_key)
			if user:
				# Sign the user in.
				User = get_user_model()
				this_user = User.objects.get(email__iexact=user.email)
				this_user.backend = 'django.contrib.auth.backends.ModelBackend'
				login(request, user=this_user)
				redirect_to = reverse('profile')
				return redirect(redirect_to)
			else:
				return render(request, "activate_fail.html")
		else:
			context = {
				'activation_key': activation_key,
			}
			return render(request, "activate_retry.html", context)

	except AccountSignup.DoesNotExist:
		return render(request, "activate_fail.html")


def activate_retry(request, activation_key):
	"""
	Reissue a new ``activation_key`` for the user with the expired ``activation_key``.
	"""
	try:
		if AccountSignup.objects.check_expired_activation(activation_key):
			new_key = AccountSignup.objects.reissue_activation(activation_key)
			if new_key:
				return render(request, "activate_retry_success.html")
			else:
				return redirect(reverse('activate', args=(activation_key,)))
		else:
			return redirect(reverse('activate', args=(activation_key,)))
	except AccountSignup.DoesNotExist:
		return redirect(reverse('activate', args=(activation_key,)))