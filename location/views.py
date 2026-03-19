from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import AddressForm
from django.views.generic import ListView
from .models import Address
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required


class AddressCreateView(LoginRequiredMixin, CreateView):
    form_class = AddressForm
    template_name = 'location/add_address.html'
    def get_success_url(self):
        from django.urls import reverse
        return reverse('profile_settings') + '#locations'

    def form_valid(self, form):
        address = form.save(commit=False)
        address.user = self.request.user
        address.save()
        return super().form_valid(form)
    
class AddressListView(LoginRequiredMixin, ListView):
    model = Address
    template_name = 'location/address_list.html'
    context_object_name = 'addresses'

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
    
class AddressUpdateView(LoginRequiredMixin, UpdateView):
    model = Address
    fields = ['street', 'city', 'state', 'pincode', 'latitude', 'longitude']
    template_name = 'location/add_address.html'
    def get_success_url(self):
        from django.urls import reverse
        return reverse('profile_settings') + '#locations'

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


@login_required
def delete_address(request, pk):
    address = get_object_or_404(
        Address,
        pk=pk,
        user=request.user
    )
    address.delete()
    from django.urls import reverse
    return redirect(reverse('profile_settings') + '#locations')