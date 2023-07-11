from rest_framework import serializers
from .models import tweets


class tweetsSerializers(serializers.ModelSerializer):
    class Meta:
        model = tweets
        fields='__all__'