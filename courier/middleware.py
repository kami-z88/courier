from __future__ import absolute_import, division, print_function
try:
	from threading import local
except ImportError:
	from django.utils._threading_local import local

_thread_locals = local()


def get_current_request():
	""" returns the request object for this thread """
	return getattr(_thread_locals, "request", None)


def get_current_user():
	""" returns the current user, if exist, otherwise returns None """
	request = get_current_request()
	if request:
		return getattr(request, "user", None)


class ThreadLocalMiddleware(object):
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		response = self.get_response(request)
		return response

	def process_view(self, request, view_func, view_args, view_kwargs):
		if request.user.is_authenticated:
			from courier.models import Dispatcher, Courier
			if Dispatcher.objects.filter(user=request.user).exists():
				request.user.is_dispatcher = True
				request.user.role = "dispatcher"
				request.user.is_courier = False
				request.user.is_user = False
			elif Courier.objects.filter(user=request.user).exists():
				request.user.is_courier = True
				request.user.role = "courier"
				request.user.is_dispatcher = False
				request.user.is_user = False,
			else:
				request.user.is_user = True
				request.user.role = "user"
				request.user.is_dispatcher = False
				request.user.is_courier = False

			_thread_locals.request = request

	def process_request(self, request):
		_thread_locals.request = request

	def process_response(self, request, response):
		if hasattr(_thread_locals, 'request'):
			del _thread_locals.request
		return response

