from django.urls import path, include

from rest_framework.routers import DefaultRouter

from product import views

router = DefaultRouter()
router.register('products', views.ProductViewSet)
router.register('tags', views.TagViewSet)
router.register('category', views.CategoryViewSet)

app_name = 'product'

urlpatterns = [
    path('', include(router.urls)),
    path('product/<str:name>/', views.ProductReviewViewSet.as_view(), name='product-review'),
]
