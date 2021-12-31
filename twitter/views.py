from django.views.generic import ListView, TemplateView, View
from django.views.generic.edit import CreateView, DeleteView
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls.base import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.utils.http import urlencode
from .models import FavoriteRelation, User, Tweet, FollowRelation, TweetClosure
from .forms import UserCreationForm
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone

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

        context.update({
            'tweet_list': tweet_list,
            'favorite_list': favorite_list,
        })
        return context
        
#ツイート用
class TweetView(LoginRequiredMixin,TemplateView):
    template_name = 'twitter/tweet.html'

    def post(self, request, **kwargs):
        #ツイート時間を取得
        pub_date = timezone.now()
        #ツイートテーブルに登録
        reply_tweet = Tweet.objects.create(user=self.request.user, pub_date=pub_date, tweet_text=request.POST.get('tweet_text'))
        #リプライツイートのpk取得
        reply_pk = reply_tweet.pk
        #閉包テーブルに登録
        TweetClosure.objects.create(ancestor=reply_pk,descendant=reply_pk,path_length='0')
        #詳細画面にリダイレクト
        return redirect('home')

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
        
        #ユーザがフォロー済みか判別するフラグを取得
        is_followed = FollowRelation.objects.filter(follower=self.request.user, followee=followee).exists()
         
        #選択したユーザのpkを取得
        followee_pk = self.request.GET.get('user_pk')
        #選択したユーザのツイート情報
        #ソート条件：-投稿時間
        tweet_list = Tweet.objects.select_related('user').filter(user__pk = followee_pk).order_by('-pub_date')
        #お気に入り登録済みのツイートを取得
        favorite_list = tweet_list.filter(favorite_tweet__favorite_user=self.request.user)

        context.update({
            'user': followee,
            'is_followed': is_followed,
            'tweet_list': tweet_list,
            'favorite_list': favorite_list,
        })

        return context

#お気に入り登録用
class FollowView(LoginRequiredMixin,View):
    def post(self, request, **kwargs):
        #フォローするユーザのユーザテーブルのpkを取得
        followee_pk = request.POST.get('followee_pk')
        #フォローするユーザのユーザ情報を取得
        followee = get_object_or_404(User, pk=followee_pk)
        #フォロー関連テーブルに登録
        FollowRelation(follower=self.request.user, followee=followee).save()

        return JsonResponse(data={})

#フォロー解除用
class DeleteFollowView(LoginRequiredMixin,TemplateView):
    def post(self, request, **kwargs):
        #フォロー解除するユーザのユーザテーブルのpkを取得
        followee_pk = request.POST.get('followee_pk')
        #フォロー解除するユーザ情報を取得
        followee = get_object_or_404(User, pk=followee_pk)
        #フォロー関連テーブルからレコード削除
        FollowRelation.objects.get(follower=self.request.user, followee=followee).delete()

        return JsonResponse(data={})

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

#リプライ用
class ReplyView(LoginRequiredMixin,TemplateView):
    template_name = 'twitter/reply.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #選択したユーザのpkを取得
        tweet_pk = self.request.GET.get('tweet_pk')

        context.update({
            'tweet_pk': tweet_pk,
        })

        return context
    def post(self, request, **kwargs):
        #ツイート時間を取得
        pub_date = timezone.now()
        #ツイートテーブルに登録
        Tweet.objects.create(user=self.request.user, pub_date=pub_date, tweet_text=request.POST.get('tweet_text'))

        #リプライツイートを取得
        reply_tweet = Tweet.objects.get(user=self.request.user, pub_date=pub_date, tweet_text=request.POST.get('tweet_text'))

        #自己参照レコードを閉包テーブルに登録
        TweetClosure.objects.create(ancestor=reply_tweet,descendant=reply_tweet,path_length='0')

        #リプライツイートの先祖ツイートを取得
        tweetclosures = TweetClosure.objects.select_related('descendant').filter(descendant__pk=request.POST.get('tweet_pk'))

        #ツイート閉包テーブルに登録するレコードを作成
        add_tweetclosures = [] 
        for tweetclosure in tweetclosures:
            element = TweetClosure(ancestor=tweetclosure.ancestor,descendant=reply_tweet,path_length=tweetclosure.path_length + 1)
            add_tweetclosures.append(element)
        
        #ツイート閉包テーブルにレコードをまとめてインサート
        TweetClosure.objects.bulk_create(add_tweetclosures)
       
        #リプライ画面の遷移前画面にリダイレクト        
        return redirect(self.request.POST.get('before_page'))


#ツイート詳細画面
class TweetDetailView(LoginRequiredMixin,TemplateView):
    template_name = 'twitter/tweet_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #選択したツイートを取得
        tweet_pk = self.request.GET.get('tweet_pk')
        tweet = Tweet.objects.get(pk=tweet_pk)
        
        #先祖レコードを取得
        ancestor_tweet_list = tweet.ancestor_tweets.all().order_by('pub_date')

        #お気に入り登録済みのツイートを取得
        favorite_list = Tweet.objects.filter(favorite_tweet__favorite_user=self.request.user)

        #深さ1の子孫レコードを取得
        descendant_tweet_list = TweetClosure.objects.select_related('ancestor','descendant').filter(ancestor=tweet, path_length='1').order_by('descendant__pub_date')

        context.update({
            'ancestor_tweet_list': ancestor_tweet_list,
            'descendant_tweet_list': descendant_tweet_list,
            'favorite_list': favorite_list,
        })
        return context