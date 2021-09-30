from django.views.generic import ListView, TemplateView, View
from django.views.generic.edit import CreateView, DeleteView
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls.base import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.utils.http import urlencode
from .models import FavoriteRelation, User, Tweet, FollowRelation
from .forms import UserCreationForm, TweetForm
from django.db.models import Q
from django.http import JsonResponse

# Create your views here.
#ユーザ登録画面
class  AccountRegistration(CreateView):
    form_class = UserCreationForm
    template_name = 'twitter/register.html'
    success_url = reverse_lazy('login')

#ログイン画面
class LoginView(LoginView):
    form_class = AuthenticationForm
    template_name = 'twitter/login.html'
    success_url = reverse_lazy('home')

#ホーム画面
class HomeView(LoginRequiredMixin,TemplateView):
    template_name = 'twitter/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #ログインユーザのフォロー中ユーザを取得
        followees = self.request.user.followees.all()

        #ログインユーザとフォロー中ユーザのツイートを取得
        tweet_list = Tweet.objects.select_related('user').filter(Q(user = self.request.user) | Q(user__in = followees)).order_by('-pub_date')

        #お気に入り登録済みのツイートを取得
        favorite_list = tweet_list.filter(favorite_tweet__favorite_user=self.request.user)

        context={
            'tweet_list': tweet_list,
            'favorite_list': favorite_list,
        }
        return context
        
#ツイート画面
class  TweetView(LoginRequiredMixin,CreateView):
    form_class = TweetForm
    template_name = 'twitter/tweet.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

#ユーザ検索画面
class SearchUserView(LoginRequiredMixin,ListView):
    template_name = 'twitter/search_user.html'
    context_object_name = 'user_list'

    def get_queryset(self):
        #検索ユーザ名を取得
        search_username = self.request.GET.get('search_username')
        
        if search_username:
            #検索時
            #検索条件：ログインユーザ以外、検索ユーザ名と部分一致
            #ソート条件：ユーザ名
            return User.objects.exclude(username = self.request.user.username).filter(username__icontains = search_username).order_by('username')
        else:
            #初期表示
            #検索条件：ログインユーザ以外
            #ソート条件：ユーザ名
            return User.objects.exclude(username = self.request.user.username).order_by('username')

#ユーザ詳細画面
class UserDetailView(LoginRequiredMixin,TemplateView):
    template_name = 'twitter/user_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #選択したユーザのpkを取得
        followee_pk = self.request.GET.get('user_pk')
        #選択したユーザの情報を取得
        followee = get_object_or_404(User, pk=followee_pk)
        #選択したユーザのユーザ情報をcontextに格納
        context['user'] = followee
        
        #ユーザがフォロー済みか判別するフラグをcontextに追加
        #１：フォロー済み、２：未フォロー
        if FollowRelation.objects.select_related('follower','followee').filter(follower=self.request.user, followee=followee):
            context['is_followed'] = '1'
        else:
            context['is_followed'] = '0'

        #選択したユーザのpkを取得
        followee_pk = self.request.GET.get('user_pk')
        #選択したユーザのツイート情報
        #ソート条件：-投稿時間
        tweet_list = Tweet.objects.select_related('user').filter(user__pk = followee_pk).order_by('-pub_date')
        #お気に入り登録済みのツイートを取得
        favorite_list = tweet_list.filter(favorite_tweet__favorite_user=self.request.user)

        context={
            'tweet_list': tweet_list,
            'favorite_list': favorite_list,
        }

        return context

#フォロー用
class FollowView(LoginRequiredMixin,TemplateView):
    def post(self, request, **kwargs):
        #フォローするユーザのユーザテーブルのpkを取得
        followee_pk = request.POST.get('followee_pk')
        #フォローするユーザのユーザ情報を取得
        followee = get_object_or_404(User, pk=followee_pk)
        #フォロー関連テーブルに登録
        FollowRelation(follower=self.request.user, followee=followee).save()

        #詳細画面にリダイレクト
        redirect_url = reverse('user_detail')
        parameters = urlencode(dict(user_pk=followee_pk))
        url = f'{redirect_url}?{parameters}'
        return redirect(url)

#フォロー解除用
class DeleteFollowView(LoginRequiredMixin,TemplateView):
    def post(self, request, **kwargs):
        #フォロー解除するユーザのユーザテーブルのpkを取得
        followee_pk = request.POST.get('followee_pk')
        #フォロー解除するユーザ情報を取得
        followee = get_object_or_404(User, pk=followee_pk)
        #フォロー関連テーブルからレコード削除
        FollowRelation.objects.get(follower=self.request.user, followee=followee).delete()

        #詳細画面にリダイレクト
        redirect_url = reverse('user_detail')
        parameters = urlencode(dict(user_pk=followee_pk))
        url = f'{redirect_url}?{parameters}'
        return redirect(url)

#フォロー画面
class FollowUserListView(LoginRequiredMixin,ListView):
    template_name = 'twitter/follow_user_list.html'
    context_object_name = 'user_list'

    def get_queryset(self):
        #検索ユーザ名を取得
        search_username = self.request.GET.get('search_username')
        
        if search_username:
            #検索時
            return FollowRelation.objects.select_related('follower','followee').filter(follower = self.request.user,followee__username__icontains=search_username).order_by('followee__username')
        else:
            #初期表示
            return FollowRelation.objects.select_related('follower','followee').filter(follower = self.request.user).order_by('followee__username')

#フォロワー画面
class FollowedUserListView(LoginRequiredMixin,ListView):
    template_name = 'twitter/followed_user_list.html'
    context_object_name = 'user_list'

    def get_queryset(self):
        #検索ユーザ名を取得
        search_username = self.request.GET.get('search_username')
        
        if search_username:
            #検索時
            return FollowRelation.objects.select_related('follower','followee').filter(followee = self.request.user,followees__username__icontains=search_username).order_by('followee__username')
        else:
            #初期表示
            return FollowRelation.objects.select_related('follower','followee').filter(followee = self.request.user).order_by('follower__username')

#お気に入り画面
class FavoriteTweetListView(LoginRequiredMixin,ListView):
    template_name = 'twitter/favorite_tweet_list.html'
    context_object_name = 'favorite_relation_list'

    def get_queryset(self):
        #検索ユーザ名を取得
        search_username = self.request.GET.get('search_username')
        
        if search_username:
            #検索時
            return FavoriteRelation.objects.select_related('favorite_user','favorite_tweet__user').filter(favorite_user = self.request.user, fovorite_tweet__user__username = search_username).order_by('favorite_tweet__pub_date')
        else:
            #初期表示
            return FavoriteRelation.objects.select_related('favorite_user','favorite_tweet__user').filter(favorite_user = self.request.user).order_by('favorite_tweet__pub_date')

#お気に入り登録用
class RegisterFavoriteTweetView(LoginRequiredMixin,View):
    def post(self, request, **kwargs):
        #お気に入りするツイートのpkを取得
        tweet_pk = request.POST.get('tweet_pk')
        #お気に入りするツイートのインスタンスを取得
        try:
            tweet = Tweet.objects.get(pk=tweet_pk)
        except Tweet.DoesNotExist:
            return JsonResponse(data={},status=404)

        #お気に入り関連テーブルに登録
        FavoriteRelation(favorite_user=self.request.user, favorite_tweet=tweet).save()

        return JsonResponse(data={})

#お気に入り削除用
class DeleteFavoriteTweetView(LoginRequiredMixin,View):
    def post(self, request, **kwargs):
        #お気に入りから外すツイートのpkを取得
        tweet_pk = request.POST.get('tweet_pk')
        #お気に入りから外すツイートのインスタンスを取得
        try:
            tweet = Tweet.objects.get(pk=tweet_pk)
        except Tweet.DoesNotExist:
            return JsonResponse(data={},status=404)

        #お気に入り関連テーブルから削除
        FavoriteRelation.objects.get(favorite_user=self.request.user, favorite_tweet=tweet).delete()

        return JsonResponse(data={})