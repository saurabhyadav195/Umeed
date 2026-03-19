import random
from django.views.generic import FormView, CreateView, ListView, TemplateView
from django import forms
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import redirect
from .forms import SignupForm, DocumentUploadForm
from .models import EmailOTP, VerificationDocument, Notification
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
from accounts.utils import send_push_notification
from location.models import Address

User = get_user_model()

class HomeView(TemplateView):
    template_name = 'home.html'

class AboutView(TemplateView):
    template_name = 'about.html'

class PrivacyPolicyView(TemplateView):
    template_name = 'privacy_policy.html'

class TermsOfServiceView(TemplateView):
    template_name = 'terms_of_service.html'

class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        from accounts.models import User
        from donations.models import Donation
        context = super().get_context_data(**kwargs)
        context['active_ngos'] = User.objects.filter(role='ngo', is_active=True).count()
        context['active_restaurants'] = User.objects.filter(role='restaurant', is_active=True).count()
        # Since quantity is a CharField, we estimate meals by completed donations
        completed_donations = Donation.objects.filter(status='completed').count()
        context['meals_recovered'] = completed_donations * 25  # Estimated 25 meals per donation
        return context
    
class SignupView(FormView):
    template_name = 'accounts/signup.html'
    form_class = SignupForm
    success_url = reverse_lazy('verify_otp')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.is_active = False
        user.email_verified = False
        user.save()

        otp_code = str(random.randint(100000, 999999))

        EmailOTP.objects.create(
            user=user,
            otp=otp_code
        )

        send_mail(
            'Your OTP Verification Code',
            f'Your OTP is {otp_code}',
            None,
            [user.email],
        )

        self.request.session['user_id'] = user.id

        return super().form_valid(form)
    

class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6)

class VerifyOTPView(FormView):
    template_name = 'accounts/verify_otp.html'
    form_class = OTPForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user_id = self.request.session.get('user_id')
        otp_input = form.cleaned_data['otp']

        otp_record = EmailOTP.objects.filter(
            user_id=user_id,
            otp=otp_input,
            is_used=False
        ).first()

        if otp_record and not otp_record.is_expired():
            otp_record.is_used = True
            otp_record.save()

            user = otp_record.user
            user.is_active = True
            user.email_verified = True
            user.save()

            return super().form_valid(form)

        form.add_error(None, "Invalid or expired OTP")
        return self.form_invalid(form)
    
class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'

    def get_success_url(self):
        user = self.request.user

        if user.role == 'restaurant':
            return reverse_lazy('restaurant_dashboard')
        else:
            return reverse_lazy('ngo_dashboard')
        
class DocumentUploadView(LoginRequiredMixin, CreateView):
    model = VerificationDocument
    form_class = DocumentUploadForm
    template_name = 'accounts/upload_document.html'
    
    def get_success_url(self):
        from django.urls import reverse
        return reverse('profile_settings') + '#documents'

    def form_valid(self, form):
        doc = form.save(commit=False)
        doc.user = self.request.user
        doc.save()
        return super().form_valid(form)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        if self.request.user.role == 'restaurant':
            form.fields['document_type'].choices = [
                ('fssai', 'FSSAI License'),
                ('business_registration', 'Business Registration'),
            ]
        else:
            form.fields['document_type'].choices = [
                ('ngo_registration', 'NGO Registration Certificate'),
                ('food_storage', 'Food Storage License'),
            ]

        return form


class DocumentListView(LoginRequiredMixin, ListView):
    model = VerificationDocument
    template_name = 'accounts/document_list.html'
    context_object_name = 'documents'

    def get_queryset(self):
        return VerificationDocument.objects.filter(user=self.request.user)

class ProfileSettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile_settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['addresses'] = Address.objects.filter(user=self.request.user)
        context['documents'] = VerificationDocument.objects.filter(user=self.request.user)
        return context


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'accounts/notifications.html'
    context_object_name = 'notifications'

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user
        ).order_by('-created_at')
    
@login_required
def unread_notifications(request):
    notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by('-created_at')

    data = [
        {
            "id": n.id,
            "message": n.message
        }
        for n in notifications
    ]

    return JsonResponse({"notifications": data})

@login_required
def mark_notification_read(request, pk):
    notification = Notification.objects.filter(
        pk=pk,
        user=request.user
    ).first()

    if notification:
        notification.is_read = True
        notification.save()

    return JsonResponse({"status": "ok"})

@login_required
@csrf_exempt
def save_fcm_token(request):

    if request.method == "POST":

        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        token = data.get("token")

        if not token:
            return JsonResponse({"error": "Token is required"}, status=400)

        # Clear this token from any other accounts (useful for testing multiple accounts on the same browser)
        request.user.__class__.objects.filter(fcm_token=token).exclude(id=request.user.id).update(fcm_token=None)

        request.user.fcm_token = token
        request.user.save(update_fields=['fcm_token'])

        return JsonResponse({"status": "token saved"})

    return JsonResponse({"error": "Method not allowed"}, status=405)


def test_push(request):

    send_push_notification(
        request.user,
        "Test Notification",
        "Firebase push working!"
    )

    return HttpResponse("sent")