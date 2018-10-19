import datetime, os
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import ugettext_lazy as _


# used to get logo directory based on user's id
def get_logo_path(instance, filename):
	name, ext = os.path.splitext(filename)
	filename = 'logo{}'.format(ext)
	return "logo/{0}".format(filename)


class SiteSettings(models.Model):
	site = models.OneToOneField(Site, related_name='site', on_delete=models.CASCADE)
	favicon = models.ImageField(_('Browser icon of the website'),upload_to=get_logo_path, blank=True, null=True)
	minimal_logo = models.ImageField(_('small, square sized logo for mobile view'),upload_to=get_logo_path, blank=True, null=True)
	logo = models.ImageField(_('Logo for site header'),upload_to=get_logo_path, blank=True, null=True)
	large_logo = models.ImageField(_('Large logo for pages like login & signup'),upload_to=get_logo_path, blank=True, null=True)
	brand_name = models.CharField(_('Site header name'), max_length=128, blank=True, default='Courier App')
	tracking_id_prefix = models.CharField(_('Prefix for Tracking ID'), max_length=16, blank=True, null=True)
	tracking_id_suffix = models.CharField(_('Suffix for Tracking ID'), max_length=16, blank=True, null=True)
