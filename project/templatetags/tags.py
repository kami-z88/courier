from django import template
from account.models import Profile
from sorl.thumbnail import get_thumbnail
from django.contrib.sites.models import Site
from settings.models import SiteSettings
from courier.models import Courier, Dispatcher
register = template.Library()


@register.simple_tag(takes_context=True)
def logged_in_user_avatar(context, size="200x200",):
	"""
	:return user's profile avatar
	"""
	if context['request'].user.is_authenticated:
		profile = Profile.objects.get(user=context['request'].user)
		avatar = profile.get_avatar_url(size=128)
		im = get_thumbnail(avatar, "128x128", crop='center', quality=99)
		return "/files/{}".format(im.name)
		return avatar
	else:
		return False


@register.simple_tag(takes_context=True)
def site_favicon(context):
	"""
	:return Site FavIcon
	"""
	current_site = Site.objects.get_current()
	site_settings = SiteSettings.objects.get(site=current_site)

	return site_settings.favicon.url


@register.simple_tag(takes_context=True)
def site_logo(context):
	"""
	:return Site logo or brand name
	"""
	current_site = Site.objects.get_current()
	site_settings = SiteSettings.objects.get(site=current_site)

	if site_settings.logo:
		from django.utils.safestring import mark_safe
		return mark_safe('<img src="{}"/>'.format(site_settings.logo.url))
	else:
		return site_settings.brand_name


@register.simple_tag(takes_context=True)
def site_large_logo(context):
	"""
	:return Site banner logo
	"""
	current_site = Site.objects.get_current()
	site_settings = SiteSettings.objects.get(site=current_site)

	if site_settings.logo:
		from django.utils.safestring import mark_safe
		return mark_safe('<img src="{}"/>'.format(site_settings.large_logo.url))
	else:
		return site_settings.brand_name


@register.simple_tag(takes_context=True)
def site_minimal_logo(context):
	"""
	:return Site's mobile view logo
	"""
	current_site = Site.objects.get_current()
	site_settings = SiteSettings.objects.get(site=current_site)

	if site_settings.logo:
		from django.utils.safestring import mark_safe
		return mark_safe('<img src="{}"/>'.format(site_settings.minimal_logo.url))
	else:
		return site_settings.brand_name


@register.filter(name='field_type')
def field_type(field):
	"""
	Get form field's type, usage:
	{{form.field_name|field_type}}
	:return: charfield, urlfield, typedchoicefield, imagefield, emailfield ...
	"""
	return field.field.widget.__class__.__name__


@register.filter
def get_item(dictionary, key):
	return dictionary.get(key)