from django import forms
from .models import User, Tweet
from django.contrib.auth.forms import UserCreationForm

class UserCreationForm(UserCreationForm):

  class Meta:
    model = User
    fields = ('username','password1','password2',) 

class TweetForm(forms.ModelForm):
  class Meta:
    model = Tweet
    fields = ('tweet_text',)

    widgets = {
      'tweet_text': forms.Textarea(attrs={'class':'tweet_input_text',}),
    }