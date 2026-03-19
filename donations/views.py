from django.views.generic import CreateView, ListView, UpdateView, DeleteView, TemplateView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Donation, DonationRequest, DonationQuery
from .forms import DonationForm
from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from location.models import Address
from location.utils import haversine
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import Notification
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from accounts.utils import send_push_notification

class DonationCreateView(LoginRequiredMixin, CreateView):
    model = Donation
    form_class = DonationForm
    template_name = 'donations/create_donation.html'
    success_url = reverse_lazy('restaurant_donations')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        donation = form.save(commit=False)
        donation.restaurant = self.request.user
        donation.save()
        
        # Find NGOs near this donation
        ngo_bases = Address.objects.filter(user__role='ngo')

        notified_users = set()

        for base in ngo_bases:

            distance = haversine(
                donation.address.latitude,
                donation.address.longitude,
                base.latitude,
                base.longitude
            )

            if distance <= 10:  # 10km radius

                ngo_user = base.user

                if ngo_user.id in notified_users:
                    continue

                notified_users.add(ngo_user.id)

                # Create notification
                send_push_notification(
                    ngo_user,
                    "New Donation Nearby",
                    f"{donation.food_name} available {round(distance,2)} km away."
                )

                # Send email alert
                send_mail(
                    subject="New Food Donation Near You",
                    message=f"""
    Hello {ngo_user.organization_name},

    A new food donation is available near your location.

    Food: {donation.food_name}
    Restaurant: {donation.restaurant.organization_name}
    Distance: {round(distance,2)} km

    Login to request the donation.
    """,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[ngo_user.email],
                    fail_silently=True,
                )

        return super().form_valid(form)
        
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_verified:
            messages.error(request, "Your account is not verified. Please upload required documents.")
            return redirect('restaurant_dashboard')
        return super().dispatch(request, *args, **kwargs)

class RestaurantDonationListView(LoginRequiredMixin, ListView):
    model = Donation
    template_name = 'donations/restaurant_donations.html'
    context_object_name = 'donations'

    def get_queryset(self):
        return Donation.objects.filter(
            restaurant=self.request.user
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context
    
class DonationUpdateView(LoginRequiredMixin, UpdateView):
    model = Donation
    form_class = DonationForm
    template_name = 'donations/create_donation.html'
    success_url = reverse_lazy('restaurant_donations')

    def get_queryset(self):
        return Donation.objects.filter(restaurant=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

@login_required
def delete_donation(request, pk):
    donation = get_object_or_404(
        Donation,
        pk=pk,
        restaurant=request.user
    )
    donation.delete()
    return redirect('restaurant_donations')

class NGONearbyDonationsView(LoginRequiredMixin, TemplateView):
    template_name = 'donations/ngo_nearby.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        base_id = self.request.GET.get('base')

        radius = int(self.request.GET.get('radius', 10))
        context['radius'] = radius
        
        bases = Address.objects.filter(user=user)
        context['bases'] = bases

        nearby_donations = []

        if base_id:
            base = Address.objects.get(id=base_id, user=user)

            from .models import Donation

            donations = Donation.objects.filter(
                status='available',
                expiry_time__gt=timezone.now()
            )

            for donation in donations:
                distance = haversine(
                    base.latitude,
                    base.longitude,
                    donation.address.latitude,
                    donation.address.longitude
                )

                if distance <= radius:  # Only include donations within the specified radius
                    nearby_donations.append({
                        'donation': donation,
                        'distance': round(distance, 2)
                    })

            nearby_donations.sort(key=lambda x: x['distance'])

        context['nearby_donations'] = nearby_donations
        context['selected_base'] = base_id

        return context
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_verified:
            messages.error(request, "Your account is not verified. Please upload required documents.")
            return redirect('ngo_dashboard')
        return super().dispatch(request, *args, **kwargs)

@login_required
def request_donation(request, pk):
    donation = get_object_or_404(
        Donation,
        pk=pk,
        expiry_time__gt=timezone.now()
    )

    if DonationRequest.objects.filter(
        donation=donation,
        ngo=request.user
    ).exists():
        messages.warning(request, "You already requested this donation.")
        return redirect('ngo_nearby')

    DonationRequest.objects.create(
        donation=donation,
        ngo=request.user
    )

    Notification.objects.create(
        user=donation.restaurant,
        message=f"{request.user.organization_name} requested your donation."
    )

    send_push_notification(
        donation.restaurant,
        "New Donation Request",
        f"{request.user.organization_name} requested your donation."
    )

    messages.success(request, "Donation requested successfully.")
    return redirect('ngo_nearby')

class RestaurantRequestsView(LoginRequiredMixin, ListView):
    model = DonationRequest
    template_name = 'donations/restaurant_requests.html'
    context_object_name = 'requests'

    def get_queryset(self):
        return DonationRequest.objects.filter(
            donation__restaurant=self.request.user
        ).order_by('-requested_at')

@login_required
def accept_request(request, pk):
    req = get_object_or_404(
        DonationRequest,
        pk=pk,
        donation__restaurant=request.user
    )

    donation = req.donation

    # Accept selected request
    req.status = 'accepted'
    req.save()

    send_mail(
        subject="Donation Request Accepted",
        message=f"""
        Hello {req.ngo.organization_name},

        Your request for donation '{req.donation.food_name}' has been accepted.

        Please coordinate pickup with the restaurant.

        Thank you.
        """,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[req.ngo.email],
        fail_silently=True,
    )

    Notification.objects.create(
        user=req.ngo,
        message=f"Your request for '{req.donation.food_name}' was accepted."
    )

    send_push_notification(
        req.ngo,
        "Donation Request Accepted",
        f"Your request for {req.donation.food_name} was accepted."
    )

    # Reject all other requests automatically
    DonationRequest.objects.filter(
        donation=donation
    ).exclude(pk=req.pk).update(status='rejected')

    donation.status = 'accepted'
    donation.save()

    messages.success(request, "Request accepted.")
    return redirect('restaurant_requests')


@login_required
def reject_request(request, pk):
    req = get_object_or_404(DonationRequest, pk=pk, donation__restaurant=request.user)

    req.status = 'rejected'
    req.save()

    req.donation.status = 'available'
    req.donation.save()

    Notification.objects.create(
        user=req.ngo,
        message=f"Your request for '{req.donation.food_name}' was rejected."
    )

    send_push_notification(
        req.ngo,
        "Donation Request Rejected",
        f"Your request for {req.donation.food_name} was rejected."
    )

    messages.info(request, "Request rejected.")
    return redirect('restaurant_requests')

class NGORequestsView(LoginRequiredMixin, ListView):
    model = DonationRequest
    template_name = 'donations/ngo_requests.html'
    context_object_name = 'requests'

    def get_queryset(self):
        return DonationRequest.objects.filter(
            ngo=self.request.user
        ).order_by('-requested_at')
    
@login_required
def complete_donation(request, pk):
    donation = get_object_or_404(
        Donation,
        pk=pk
    )

    # Only restaurant or accepted NGO can complete
    if donation.restaurant == request.user or \
       DonationRequest.objects.filter(
           donation=donation,
           ngo=request.user,
           status='accepted'
       ).exists():

        donation.status = 'completed'
        donation.save()

        messages.success(request, "Donation marked as completed.")
    else:
        messages.error(request, "You are not authorized to complete this donation.")

    return redirect(request.META.get('HTTP_REFERER', '/'))

class DonationQueryView(LoginRequiredMixin, DetailView):
    model = Donation
    template_name = 'donations/donation_query.html'
    context_object_name = 'donation'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        donation = self.get_object()

        # Only allow if accepted
        if donation.status != 'accepted':
            context['queries'] = []
            context['chat_disabled'] = True
        else:
            context['queries'] = DonationQuery.objects.filter(
                donation=donation
            ).order_by('created_at')
            context['chat_disabled'] = False

        return context
    
@login_required
def send_query(request, pk):
    donation = Donation.objects.get(pk=pk)

    if donation.status != 'accepted':
        return JsonResponse({"error": "Not allowed"}, status=403)

    message = request.POST.get("message")

    if message:
        query = DonationQuery.objects.create(
            donation=donation,
            sender=request.user,
            message=message
        )

        # Create notification for other user
    
        if request.user == donation.restaurant:
            target = DonationRequest.objects.get(
                donation=donation,
                status='accepted'
            ).ngo
        else:
            target = donation.restaurant

        Notification.objects.create(
            user=target,
            message=f"New message regarding '{donation.food_name}'."
        )

        send_push_notification(
            target,
            "New Message",
            f"New message regarding '{donation.food_name}'."
        )

        return JsonResponse({"status": "ok"})

    return JsonResponse({"error": "Empty message"}, status=400)

@login_required
def get_queries(request, pk):

    queries = DonationQuery.objects.filter(
        donation_id=pk
    ).order_by("created_at")

    data = []

    for q in queries:

        data.append({
            "sender": q.sender.organization_name,
            "message": q.message,
            "time": q.created_at.strftime("%H:%M")
        })

    return JsonResponse({"messages": data})

