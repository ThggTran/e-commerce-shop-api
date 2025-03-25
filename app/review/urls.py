from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReviewViewSet

router = DefaultRouter()
router.register('products/(?P<product_id>\d+)/reviews', ReviewViewSet, basename='product-reviews')

app_name = 'review'

urlpatterns = [
    path('', include(router.urls)),
]
