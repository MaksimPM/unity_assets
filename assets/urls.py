from django.urls import path

from assets.apps import AssetsConfig
from assets.views import UnityAssetsListAPIView, UnityAssetRetrieveAPIView

app_name = AssetsConfig.name

urlpatterns = [
    path('list/', UnityAssetsListAPIView.as_view(), name='unity_assets'),
    path('<int:pk>/detail/', UnityAssetRetrieveAPIView.as_view(), name='unity_asset'),
]
