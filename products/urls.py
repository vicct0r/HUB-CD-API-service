from django.urls import path
from .views import ProductListCreateView, ProductComparsionListView, ProductRetrieveUpdateView, ProductRequestHUBView, ProductPatchIncrement, ProductDestroyAPIView

urlpatterns = [
    path('register/', ProductListCreateView.as_view(), name='product_register'),
    path('show-product/', ProductComparsionListView.as_view(), name='product_all'),
    path('show-product/<str:type>/', ProductComparsionListView.as_view(), name='product_find'),
    path('edit/<str:type>/', ProductRetrieveUpdateView.as_view(), name='product_edit'),
    path('request/<str:type>/<int:qtd>/', ProductRequestHUBView.as_view(), name='product_patch'),
    path('increment/<str:type>/<int:qtd>/', ProductPatchIncrement.as_view(), name='product_increment'),
    path('delete-prod/<str:type>/', ProductDestroyAPIView.as_view(), name='product_destroy')

]