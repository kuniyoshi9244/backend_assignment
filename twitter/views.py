from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls.base import reverse_lazy
from .models import Tweet
from .forms import TweetForm

# Create your views here.
class  AccountRegistration(CreateView):
    form_class = UserCreationForm
    template_name = 'twitter/register.html'
    success_url = reverse_lazy('login')

class LoginView(LoginView):
    form_class = AuthenticationForm
    template_name = 'twitter/login.html'
    success_url = reverse_lazy('home')

class HomeView(LoginRequiredMixin,ListView):
    template_name = 'twitter/home.html'
    context_object_name = 'tweet_list'

    def get_queryset(self):
        return Tweet.objects.select_related('user').filter(user = self.request.user).order_by('-pub_date')

class  TweetView(LoginRequiredMixin,CreateView):
    form_class = TweetForm
    template_name = 'twitter/tweet.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
