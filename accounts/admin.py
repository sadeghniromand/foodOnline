from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from . import models


# Register your models here.
@admin.register(models.User)
class CustomUserAdmin(UserAdmin):
    list_filter = ()
    filter_horizontal = ()
    fieldsets = ()


admin.site.register(models.UserProfile)
