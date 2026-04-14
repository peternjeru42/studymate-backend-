from rest_framework import serializers


class CurrentUserDefaultSerializerMixin:
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
