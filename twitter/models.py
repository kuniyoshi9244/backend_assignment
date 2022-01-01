from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
  followees = models.ManyToManyField(
    'User' , verbose_name='フォロー中のユーザー', through='FollowRelation', related_name='+', through_fields=('follower', 'followee')
  )
  favorite_tweets = models.ManyToManyField(
    'Tweet' , verbose_name='お気に入りのツイート', through='FavoriteRelation', related_name='favorite_user', through_fields=('favorite_user', 'favorite_tweet')
  )

class Tweet(models.Model):
  user = models.ForeignKey(User,verbose_name='ユーザ', on_delete=models.CASCADE)
  pub_date = models.DateTimeField(verbose_name='ツイート時間',default=timezone.now)
  tweet_text = models.TextField(verbose_name='ツイート内容',max_length=200)

  ancestor_tweets = models.ManyToManyField(
    'Tweet' , verbose_name='先祖レコード', through='TweetClosure', related_name='descendant_tweets', through_fields=('descendant','ancestor')
  )

class FollowRelation(models.Model):
  follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followee_relation')
  followee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower_relation')

  class Meta:
    constraints = [models.UniqueConstraint(fields=['follower','followee'],name="follow_unique"),]

class FavoriteRelation(models.Model):
  favorite_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_user')
  favorite_tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='favorite_tweet')

  class Meta:
    constraints = [models.UniqueConstraint(fields=['favorite_user','favorite_tweet'],name="favorite_unique"),]

class TweetClosure(models.Model):
  ancestor = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='descendant_tweet')
  descendant = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='ancestor_tweet')
  path_length = models.IntegerField(verbose_name='ノードからの距離')

  class Meta:
    constraints = [models.UniqueConstraint(fields=['ancestor','descendant','path_length'],name="tweetclosure_unique"),]
