from django.contrib import admin
from .models import User, Tweet, FollowRelation, FavoriteRelation

# Register your models here.
admin.site.register(User)
admin.site.register(Tweet)
admin.site.register(FollowRelation)
admin.site.register(FavoriteRelation)
