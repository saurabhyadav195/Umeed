from django.urls import path
from .views import AddressCreateView, AddressListView, AddressUpdateView, delete_address

urlpatterns = [
    path('', AddressListView.as_view(), name='address_list'),
    path('add/', AddressCreateView.as_view(), name='add_address'),
    path('edit/<int:pk>/', AddressUpdateView.as_view(), name='edit_address'),
    path('delete/<int:pk>/', delete_address, name='delete_address'),
]