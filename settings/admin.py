from settings.models import SiteSettings, ZoneSystem
from django.contrib.sites.admin import SiteAdmin
from django.contrib import admin
from django.contrib.sites.models import Site


class SiteSettingsInline(admin.StackedInline):
	model = SiteSettings
	max_num = 1


class SiteSettingsAdmin(SiteAdmin):
	inlines = [SiteSettingsInline, ]


class ZoneSystemAdmin(admin.ModelAdmin):
	list_display = ['name']

	def has_add_permission(self, request):
		base_add_permission = super(ZoneSystemAdmin, self).has_add_permission(request)
		if base_add_permission:
			# if there's already an entry, do not allow adding
			count = ZoneSystem.objects.all().count()
			if count == 0:
				return True
		return False

# Register your models here.
try:
	admin.site.unregister(Site)
except admin.sites.NotRegistered:
	pass
admin.site.register(Site, SiteSettingsAdmin)
admin.site.register(ZoneSystem, ZoneSystemAdmin)

