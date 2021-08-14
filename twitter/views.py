
from django.shortcuts import render
from django.views.generic import TemplateView #テンプレートタグ
from .forms import UserForm
from django.contrib.auth import authenticate
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.shortcuts import render

# Create your views here.
class  AccountRegistration(TemplateView):
    def __init__(self):
        self.params = {
        "AccountCreate":False,
        "user_form": UserForm(),
        }

    #Get処理
    def get(self,request):
        self.params["user_form"] = UserForm()
        self.params["AccountCreate"] = False
        return render(request,"twitter/register.html",context=self.params)
    
    #Post処理
    def post(self,request):
        self.params["user_form"] = UserForm(data=request.POST)

        #フォーム入力の有効検証
        if self.params["user_form"].is_valid():
            # アカウント情報をDB保存
            user = self.params["user_form"].save(commit=False)
            # パスワードをハッシュ化
            user.set_password(user.password)
            # ハッシュ化パスワード更新
            user.save()
            # アカウント作成情報更新
            self.params["AccountCreate"] = True

        else:
            # フォームが有効でない場合
            print(self.params["user_form"].errors)

        return render(request,"twitter/register.html",context=self.params)