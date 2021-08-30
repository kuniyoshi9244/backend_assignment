from django.contrib.auth.models import User
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls.base import reverse_lazy

# Create your views here.
class  AccountRegistration(CreateView):
    form_class = UserCreationForm
    template_name = 'twitter/register.html'
    success_url = reverse_lazy('login')

class LoginView(LoginView):
    form_class = AuthenticationForm
    template_name = 'twitter/login.html'
    success_url = reverse_lazy('home')

class HomeView(TemplateView,LoginRequiredMixin):
    template_name = 'twitter/home.html'

    def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['user_name'] = self.request.user
            return context