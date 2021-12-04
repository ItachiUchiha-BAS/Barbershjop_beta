from django.urls import path

from .views import (BaseView,
                    ProductDetailView,
                    CategoryDetalView,
                    CartView,
                    AddToCartView,
                    DeleteFromCartView,
                    ChangeQTYView)

urlpatterns = [
    path('', BaseView.as_view(), name='base'),
    path('products/<str:ct_model>/<str:slug>/', ProductDetailView.as_view(),name='product_detail'),
    path('category/<str:slug>/',CategoryDetalView.as_view(),name='category_detail'),
    path('cart/', CartView.as_view(), name='cart'),
    path('add-to-cart/<str:ct_model>/<str:slug>',AddToCartView.as_view(),name='add-to-cart'),
    path('remove-from-cart/<str:ct_model>/<str:slug>', DeleteFromCartView.as_view(), name='delete_from_cart'),
    path('change-qty/<str:ct_model>/<str:slug>', ChangeQTYView.as_view(), name='change_qty')
]