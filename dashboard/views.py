from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from donations.models import Donation

class RestaurantDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/restaurant_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        donations = Donation.objects.filter(restaurant=self.request.user)

        context['total_donations'] = donations.count()
        context['accepted_donations'] = donations.filter(status='accepted').count()
        context['completed_donations'] = donations.filter(status='completed').count()
        from django.utils import timezone
        context['available_donations'] = donations.filter(status='available', expiry_time__gt=timezone.now()).count()

        return context

class NGODashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/ngo_dashboard.html'