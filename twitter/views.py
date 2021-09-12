from django.views.generic import ListView, TemplateView
from django.views.generic.edit import CreateView, DeleteView
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls.base import reverse_lazy
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import urlencode
from .models import User, Tweet, FollowRelation
from .forms import UserCreationForm, TweetForm
from django.db.models import Q

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
class HomeView(LoginRequiredMixin,ListView):
    template_name = 'twitter/home.html'
    context_object_name = 'tweet_list'

    def get_queryset(self):
        #ログインユーザのフォロー中ユーザを取得
        followees = self.request.user.followees.all()

        #ログインユーザとフォロー中ユーザのツイートを取得
        return Tweet.objects.select_related('user').filter(Q(user = self.request.user) | Q(user__in = followees)).order_by('-pub_date')

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
class UserDetailView(LoginRequiredMixin,ListView):
    template_name = 'twitter/user_detail.html'
    context_object_name = 'tweet_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #選択したユーザのpkを取得
        followee_pk = self.request.GET.get('user_pk')
        #選択したユーザの情報を取得
        followee = User.objects.get(pk=followee_pk)
        #選択したユーザのユーザ情報をcontextに格納
        context['user'] = followee
        
        #ユーザがフォロー済みか判別するフラグをcontextに追加
        #１：フォロー済み、２：未フォロー
        if FollowRelation.objects.select_related('follower','followee').filter(follower=self.request.user, followee=followee):
            context['is_followed'] = '1'
        else:
            context['is_followed'] = '0'
        return context

    def get_queryset(self):
        #選択したユーザのpkを取得
        followee_pk = self.request.GET.get('user_pk')

        #選択したユーザのツイート情報
        #ソート条件：-投稿時間
        return Tweet.objects.select_related('user').filter(pk = followee_pk).order_by('-pub_date')

#フォロー用
class FollowView(LoginRequiredMixin,TemplateView):
    def post(self, request, **kwargs):
        #フォローするユーザのユーザテーブルのpkを取得
        followee_pk = request.POST.get('followee_pk')
        #フォローするユーザのユーザ情報を取得
        followee = User.objects.get(pk=followee_pk)
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
        #フォロー解除すりユーザ情報を取得
        followee = User.objects.get(pk=followee_pk)
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