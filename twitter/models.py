from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Tweet(models.Model):
  user = models.ForeignKey(User,verbose_name='ユーザ名', on_delete=models.CASCADE)
  pub_date = models.DateTimeField(verbose_name='ツイート時間',default=timezone.now)
  tweet_text = models.TextField(verbose_name='ツイート内容',max_length=200)