from rest_framework import serializers

from accounts.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = UserProfile.objects.create(**validated_data)
        return user


class ChangePasswordSerializer(serializers.Serializer):
    class Meta:
        model = UserProfile
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


# class EmailChangeSerializer(serializers.ModelSerializer):
#     user = UserProfileSerializer().get_fields()
#
#     class Meta:
#         model = EmailAddress
#         fields = '__all__'
