from django.urls import path
from .views import RestaurantDashboardView, NGODashboardView

urlpatterns = [
    path('restaurant/', RestaurantDashboardView.as_view(), name='restaurant_dashboard'),
    path('ngo/', NGODashboardView.as_view(), name='ngo_dashboard'),
]