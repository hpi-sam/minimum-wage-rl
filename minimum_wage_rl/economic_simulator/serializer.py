from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        # ('username', 'password')
        extra_kwargs = {'password': {'write_only': True}}