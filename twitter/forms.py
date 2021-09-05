from django import forms
from .models import Tweet

class TweetForm(forms.ModelForm):
  class Meta:
    model = Tweet
    fields = ('tweet_text',)

    widgets = {
      'tweet_text': forms.Textarea(attrs={'class':'tweet_input_text',}),
    }