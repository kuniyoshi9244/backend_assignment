from django import forms
from .models import User, Tweet
from django.contrib.auth.forms import UserCreationForm

class UserCreationForm(UserCreationForm):

  class Meta:
    model = User
    fields = ('username','password1','password2',) 