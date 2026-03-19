from django.urls import path
from .views import (DonationCreateView, 
                    RestaurantDonationListView, 
                    DonationUpdateView, 
                    delete_donation, 
                    NGONearbyDonationsView, 
                    request_donation,
                    RestaurantRequestsView,
                    accept_request,
                    reject_request,
                    NGORequestsView,
                    complete_donation,
                    DonationQueryView,
                    send_query,
                    get_queries
                    )

urlpatterns = [
    path('create/', DonationCreateView.as_view(), name='create_donation'),
    path('my/', RestaurantDonationListView.as_view(), name='restaurant_donations'),
    path('edit/<int:pk>/', DonationUpdateView.as_view(), name='edit_donation'),
    path('delete/<int:pk>/', delete_donation, name='delete_donation'),
    path('ngo/nearby/', NGONearbyDonationsView.as_view(), name='ngo_nearby'),
    path('request/<int:pk>/', request_donation, name='request_donation'),
    path('restaurant/requests/', RestaurantRequestsView.as_view(), name='restaurant_requests'),
    path('accept/<int:pk>/', accept_request, name='accept_request'),
    path('reject/<int:pk>/', reject_request, name='reject_request'),
    path('ngo/requests/', NGORequestsView.as_view(), name='ngo_requests'),
    path('complete/<int:pk>/', complete_donation, name='complete_donation'),
    path('query/<int:pk>/', DonationQueryView.as_view(), name='donation_query'),
    path('query/send/<int:pk>/', send_query, name='send_query'),
    path('query/<int:pk>/messages/', get_queries, name='get_queries'),
]