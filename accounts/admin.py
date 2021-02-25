from django.contrib import admin
from .models import UserProfile
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserProfileAdminChangeForm, UserProfileAdminCreationForm

class UserProfileAdmin(BaseUserAdmin):
    search_fields = ('email', 'first_name', 'last_name')
    list_display = ('get_full_name', 'email', 'uid', 'admin')
    list_filter = ('admin', )
    ordering = ('first_name', )
    filter_horizontal = ()

    form = UserProfileAdminChangeForm
    add_form = UserProfileAdminCreationForm

    readonly_fields = ('email', )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        return ()

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('avatar', 'first_name', 'last_name', 'phone', 'bio', 'website')}),
        ('Permissions', {'fields': ('admin', 'staff', 'active')}),
    )

    add_fieldsets = (
        ('Basic', {'fields': ('first_name', 'last_name')}),
        ('Authentication', {'fields': ('email', 'password1', 'password2')})
    )


admin.site.unregister(Group)
admin.site.register(UserProfile, UserProfileAdmin)
