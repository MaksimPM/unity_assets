from rest_framework import serializers
from .models import UnityAsset

class UnityAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnityAsset
        fields = '__all__'
