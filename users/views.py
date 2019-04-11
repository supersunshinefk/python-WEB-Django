from django.views.generic import View
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.db import IntegrityError
from django.core.cache import cache
from users.models import User
from util import constants
from util.commons import LoginRequiredMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings
import re
import json


class RegisterView(View):
    def post(self, request):
        try:
            data_dict = json.loads(request.body.decode("utf-8"))
        except Exception as e:
            context = {"code": 1, "msg": "用户名或密码不能为空"}
            return JsonResponse(context)
        try:
            username = data_dict["username"]
        except KeyError as e:
            context = {"code": 1, "msg": "用户名不能为空"}
            return JsonResponse(context)
        try:
            password = data_dict["password"]
        except KeyError as e:
            context = {"code": 1, "msg": "密码不能为空"}
            return JsonResponse(context)
        try:
            password2 = data_dict["password2"]
        except KeyError as e:
            context = {"code": 1, "msg": "密码不能为空"}
            return JsonResponse(context)
        try:
            email = data_dict["email"]
        except KeyError as e:
            context = {"code": 1, "msg": "邮箱不能为空"}
            return JsonResponse(context)
        if not all([username, password, email]):
            context = {"code": 1, "msg": "参数不完整"}
            return JsonResponse(context)
        if password != password2:
            context = {"code": 1, "msg": "两次输入的密码不一致"}
            return JsonResponse(context)
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}', str(email)):
            context = {"code": 1, "msg": "邮箱格式错误"}
            return JsonResponse(context)
        try:
            User.objects.create_user(username, email, password)
        except IntegrityError as e:
            context = {"code": 1, "msg": "用户名已存在"}
            return JsonResponse(context)
        data = {"username": username, "password": password}
        context = {"code": 0, "msg": "注册成功", "data": data}
        return JsonResponse(context)


class LoginView(View):
    def post(self, request):
        try:
            data_dict = json.loads(request.body.decode("utf-8"))
        except Exception as e:
            context = {"code": 1, "msg": "用户名或密码不能为空"}
            return JsonResponse(context)
        try:
            username = data_dict["username"]
            password = data_dict["password"]
        except KeyError as e:
            context = {"code": 1, "msg": "用户名或密码不能为空"}
            return JsonResponse(context)
        if not all([username, password]):
            context = {"code": 1, "msg": "用户名或密码不能为空"}
            return JsonResponse(context)
        user = authenticate(username=username, password=password)
        if user is None:
            context = {"code": 1, "msg": "用户名或密码错误"}
            return JsonResponse(context)
        token_name = "token_%s" % user.id
        token = cache.get(token_name)
        if token:
            cache.delete(token_name)
        token = user.generate_token(user.id, username)
        cache.set(token_name, token, timeout=constants.USER_CACHE_TOKEN_EXPIRES)
        data = {"id": user.id, "username": username}
        context = {"code": 0, "msg": "登录成功", "data": data, "token": token}
        return JsonResponse(context)


class LogoutView(View):
    def get(self, request):
        try:
            token = request.META["HTTP_AUTHORIZATION"]
        except Exception as e:
            context = {"code": 0, "msg": "用户未登录"}
            return JsonResponse(context)
        s = Serializer(settings.SECRET_KEY, constants.USER_TOKEN_EXPIRES)
        try:
            user_data = s.loads(token)
        except Exception as e:
            context = {"code": 0, "msg": "用户未登录"}
            return JsonResponse(context)
        user_id = user_data.get("user_id")
        token_name = "token_%s" % user_id
        cache_token = cache.get(token_name)
        if token != cache_token:
            context = {"code": 0, "msg": "token错误"}
            return JsonResponse(context)
        cache.delete(token_name)
        context = {"code": 0, "msg": "退出成功"}
        return JsonResponse(context)


class UserInfoView(View):
    def __init__(self):
        super(UserInfoView, self).__init__()
        self.first_name = ""
        self.last_name = ""

    def get(self, request):
        context = LoginRequiredMixin.login_required(request)
        if context["code"] != 0:
            return JsonResponse(context)
        user_id = context["user_id"]
        user = User.objects.get(id=user_id)
        username = user.username
        email = user.email
        last_login = user.last_login
        is_superuser = user.is_superuser
        first_name = user.first_name
        last_name = user.last_name
        date_joined = user.date_joined
        is_active = user.is_active
        data = {
            "username": username,
            "email": email,
            "last_login": last_login,
            "is_superuser": is_superuser,
            "first_name": first_name,
            "last_name": last_name,
            "date_joined": date_joined,
            "is_active": is_active
        }
        context = {"code": 0, "msg": "获取用户信息页面成功", "data": data}
        return JsonResponse(context)

    def put(self, request):
        context = LoginRequiredMixin.login_required(request)
        if context["code"] != 0:
            return JsonResponse(context)
        user_id = context["user_id"]
        user = User.objects.filter(id=user_id)
        try:
            data_dict = json.loads(request.body.decode("utf-8"))
        except Exception as e:
            context = {"code": 1, "msg": "获取json数据失败"}
            return JsonResponse(context)
        try:
            username = data_dict["username"]
            password = data_dict["password"]
            email = data_dict["email"]
        except Exception as e:
            context = {"code": 1, "msg": "参数不完整"}
            return JsonResponse(context)
        try:
            first_name = data_dict["first_name"]
        except Exception as e:
            first_name = self.first_name
        try:
            last_name = data_dict["last_name"]
        except Exception as e:
            last_name = self.last_name
        if not all([username, password, email]):
            context = {"code": 1, "msg": "参数不完整"}
            return JsonResponse(context)
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}', str(email)):
            context = {"code": 1, "msg": "邮箱格式错误"}
            return JsonResponse(context)
        user.password = password
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        context = {"code": 0, "msg": "用户信息修改成功"}
        return JsonResponse(context)
