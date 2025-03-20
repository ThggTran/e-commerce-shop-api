from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartItemViewSet

router = DefaultRouter()
router.register('cart', CartItemViewSet)

app_name = 'cart'

urlpatterns = [
    path('', include(router.urls)),
]