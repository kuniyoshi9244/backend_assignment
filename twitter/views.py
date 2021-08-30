from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from django.urls.base import reverse_lazy

# Create your views here.
class  AccountRegistration(CreateView):
    form_class = UserCreationForm
    template_name = 'twitter/register.html'
    success_url = reverse_lazy('registeration')