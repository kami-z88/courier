from settings.models import SiteSettings
from django.contrib.sites.admin import SiteAdmin
from django.contrib import admin
from django.contrib.sites.models import Site


class SiteSettingsInline(admin.StackedInline):
	model = SiteSettings
	max_num = 1


class SiteSettingsAdmin(SiteAdmin):
	inlines = [SiteSettingsInline, ]


# Register your models here.
try:
	admin.site.unregister(Site)
except admin.sites.NotRegistered:
	pass
admin.site.register(Site, SiteSettingsAdmin)

