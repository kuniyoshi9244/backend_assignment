from django.urls import path
from django.contrib.auth import views as av
from . import views

urlpatterns = [
    path('', views.AccountRegistration.as_view(), name='registeration'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', av.LogoutView.as_view(), name='logout'),
    path('home/',views.HomeView.as_view(), name="home"),
    path('tweet/',views.TweetView.as_view(), name="tweet"),
    path('search_user/',views.SearchUserView.as_view(), name="search_user"),
    path('user_detail/',views.UserDetailView.as_view(), name="user_detail"),
    path('follow_user_list/',views.FollowUserListView.as_view(), name="follow_user_list"),
    path('followed_user_list/',views.FollowedUserListView.as_view(), name="followed_user_list"),
    path('follow/',views.FollowView.as_view(), name="follow"),
    path('delete_follow/',views.DeleteFollowView.as_view(), name="delete_follow"),
    path('favorite_tweet_list/',views.FavoriteTweetListView.as_view(), name="favorite_tweet_list"),
    path('register_favorite_tweet/',views.RegisterFavoriteTweetView.as_view(), name="register_favorite_tweet"),
    path('delete_favorite_tweet/',views.DeleteFavoriteTweetView.as_view(), name="delete_favorite_tweet"),
    path('reply/',views.ReplyView.as_view(), name="reply"),
    path('tweet_detail/',views.TweetDetailView.as_view(), name="tweet_detail"),
    ]