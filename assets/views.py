from rest_framework.permissions import IsAuthenticated
from rest_framework import generics

from assets.models import UnityAsset
from assets.serializers import UnityAssetSerializer

class UnityAssetsListAPIView(generics.ListAPIView):
    serializer_class = UnityAssetSerializer
    permission_classes = [IsAuthenticated]
    queryset = UnityAsset.objects.all()


class UnityAssetRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = UnityAssetSerializer
    permission_classes = [IsAuthenticated]
    queryset = UnityAsset.objects.all()
