from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import user_field


class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, False)
        user_field(user, 'first_name', request.data.get('first_name'))
        user_field(user, 'last_name', request.data.get('last_name'))
        user_field(user, 'phone', request.data.get('phone'))
        user_field(user, 'avatar', request.data.get('avatar'))
        user_field(user, 'bio', request.data.get('bio'))
        user_field(user, 'website', request.data.get('website'))
        user.save()
        return user
