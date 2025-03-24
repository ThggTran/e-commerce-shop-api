from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet

router = DefaultRouter()
router.register('order', OrderViewSet, basename='order')

app_name = 'order'

urlpatterns = [
    path('', include(router.urls)),
]