from django.urls import path
from .views import (SignupView, 
                    VerifyOTPView, 
                    CustomLoginView, 
                    DocumentUploadView, 
                    DocumentListView,
                    ProfileSettingsView,
                    NotificationListView,
                    unread_notifications,
                    mark_notification_read,
                    save_fcm_token,
                    test_push)
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
    path('settings/', ProfileSettingsView.as_view(), name='profile_settings'),
    path('documents/', DocumentListView.as_view(), name='document_list'),
    path('documents/upload/', DocumentUploadView.as_view(), name='upload_document'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('notifications/', NotificationListView.as_view(), name='notifications'),
    path('api/notifications/', unread_notifications, name='unread_notifications'),
    path('api/notifications/read/<int:pk>/', mark_notification_read, name='mark_notification_read'),
    path('save-fcm-token/', save_fcm_token, name='save_fcm_token'),
    path('test_push/', test_push, name='test_push'),
]