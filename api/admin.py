from django.apps import apps
from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ['pk', 'username', 'date_joined', 'role', 'bio']
    empty_value_display = '-empty-'
    search_fields = ('username',)
    list_filter = ('date_joined', 'role',)


admin.site.register(User, UserAdmin)


class ListAdminMixin(object):
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields]
        super(ListAdminMixin, self).__init__(model, admin_site)


models = apps.get_models()
for model in models:
    admin_class = type('AdminClass', (ListAdminMixin, admin.ModelAdmin), {})
    try:
        admin.site.register(model, admin_class)
    except admin.sites.AlreadyRegistered:
        pass
