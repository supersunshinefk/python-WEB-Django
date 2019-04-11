from django.views.generic import View
from django.http import JsonResponse
from users.models import User
from util.commons import LoginRequiredMixin
from .models import Account
import re
import json


class AccountView(View):
    def __init__(self):
        super(AccountView, self).__init__()
        self.template = ""
        self.script = ""
        self.remark = ""

    def get_single_data(self, id, user_id):
        client = Account.objects.filter(id=id, account_user=user_id).first()
        client_data = dict()
        client_data["id"] = client.id
        client_data["account_id"] = client.account_id
        client_data["account_name"] = client.account_name
        client_data["account_login"] = client.account_login
        client_data["account_pin"] = client.account_pin
        client_data["template"] = client.template
        client_data["script"] = client.script
        client_data["reference"] = client.reference
        client_data["remark"] = client.remark
        client_data["version"] = client.version
        client_data["date_created"] = str(client.date_created)[:19]
        client_data["is_available"] = client.is_available
        return client_data

    def get(self, request):
        context = LoginRequiredMixin.login_required(request)
        if context["code"] != 0:
            return JsonResponse(context)
        user_id = context["user_id"]
        client_list = Account.objects.filter(account_user=user_id).order_by("id")
        if not client_list:
            context = {"code": 0, "msg": "还未有账户注册", "data": {"single_data": {}, "all_data": []}}
            return JsonResponse(context)
        id = request.GET.get("id")
        keyword = request.GET.get("keyword")
        if not keyword:
            if not id:
                id = client_list[0].id
                all_account_data = list()
                for client in client_list:
                    data_dict = dict()
                    data_dict["id"] = client.id
                    data_dict["account_id"] = client.account_id
                    data_dict["account_name"] = client.account_name
                    all_account_data.append(data_dict)
                client_data = self.get_single_data(id, user_id)
                data = {"all_data": all_account_data, "single_data": client_data}
                context = {"code": 0, "msg": "获取账户页面成功", "data": data}
                return JsonResponse(context)
            else:
                client_data = self.get_single_data(id, user_id)
                data = {"single_data": client_data}
                context = {"code": 0, "msg": "获取账户页面成功", "data": data}
                return JsonResponse(context)
        else:
            keyword = keyword.strip(" ")
            search_result = list()
            for account in client_list:
                account_dict = dict()
                if (keyword.upper() in account.account_id.upper()) or (keyword.upper() in account.account_name.upper()):
                    account_dict["id"] = account.id
                    account_dict["account_id"] = account.account_id
                    account_dict["account_name"] = account.account_name
                if account.account_name.upper() in keyword.upper():
                    account_dict["id"] = account.id
                    account_dict["account_id"] = account.account_id
                    account_dict["account_name"] = account.account_name
                if account_dict:
                    search_result.append(account_dict)
            if not search_result:
                data = {"all_data": search_result, "single_data": {}}
                context = {"code": 0, "msg": "搜索的内容不存在", "data": data}
                return JsonResponse(context)
            id = search_result[0]["id"]
            client_data = self.get_single_data(id, user_id)
            data = {"all_data": search_result, "single_data": client_data}
            context = {"code": 0, "msg": "搜索成功", "data": data}
            return JsonResponse(context)

    def post(self, request):
        context = LoginRequiredMixin.login_required(request)
        if context["code"] != 0:
            return JsonResponse(context)
        user_id = context["user_id"]
        user = User.objects.get(id=user_id)
        try:
            data_dict = json.loads(request.body.decode("utf-8"))
        except Exception as e:
            context = {"code": 1, "msg": "获取json数据失败"}
            return JsonResponse(context)
        try:
            account_id = data_dict["account_id"]
        except KeyError as e:
            context = {"code": 1, "msg": "账户标识不能为空"}
            return JsonResponse(context)
        try:
            account_name = data_dict["account_name"]
        except KeyError as e:
            context = {"code": 1, "msg": "账户名不能为空"}
            return JsonResponse(context)
        try:
            account_login = data_dict["account_login"]
        except KeyError as e:
            context = {"code": 1, "msg": "账户登录名不能为空"}
            return JsonResponse(context)
        try:
            account_pin = data_dict["account_pin"]
        except KeyError as e:
            context = {"code": 1, "msg": "账户登录密码不能为空"}
            return JsonResponse(context)
        try:
            template = data_dict["template"]
        except KeyError as e:
            template = self.template
        try:
            script = data_dict["script"]
        except KeyError as e:
            script = self.script
        try:
            remark = data_dict["remark"]
        except KeyError as e:
            remark = self.remark
        if not all([account_id, account_name, account_login, account_pin]):
            context = {"code": 1, "msg": "参数不完整"}
            return JsonResponse(context)
        try:
            tool = Account.objects.get(account_id=account_id)
        except Exception as e:
            tool = False
        if tool:
            context = {"code": 1, "msg": "account_id已存在，请重新输入"}
            return JsonResponse(context)
        if not re.match(r"^[a-zA-Z0-9_]{4,16}$", str(account_id)):
            context = {"code": 1, "msg": "账户标识为4－16位的字母,数字或下划线"}
            return JsonResponse(context)
        if not re.match(r'^[a-zA-Z0-9_]{4,16}$', str(account_login)):
            context = {"code": 1, "msg": "账户登录名为4－16位的字母,数字或下划线"}
            return JsonResponse(context)
        if not re.match(r'^[a-zA-Z0-9]{4,16}$', str(account_pin)):
            context = {"code": 1, "msg": "账户密码为6－16位的字母或数字"}
            return JsonResponse(context)
        try:
            account = Account()
            account.account_id = account_id
            account.account_name = account_name
            account.account_login = account_login
            account.account_pin = account_pin
            account.template = template
            account.script = script
            account.remark = remark
            account.account_user = user
            account.save()
        except Exception as e:
            context = {"code": 1, "msg": "数据库添加账户信息失败"}
            return JsonResponse(context)
        context = {"code": 0, "msg": "添加账户成功"}
        return JsonResponse(context)

    def put(self, request):
        context = LoginRequiredMixin.login_required(request)
        if context["code"] != 0:
            return JsonResponse(context)
        user_id = context["user_id"]
        user = User.objects.get(id=user_id)
        try:
            data_dict = json.loads(request.body.decode("utf-8"))
        except Exception as e:
            context = {"code": 1, "msg": "获取json数据失败"}
            return JsonResponse(context)
        try:
            id = data_dict["id"]
        except KeyError as e:
            context = {"code": 1, "msg": "id不能为空"}
            return JsonResponse(context)
        try:
            account_id = data_dict["account_id"]
        except KeyError as e:
            context = {"code": 1, "msg": "账户标识不能为空"}
            return JsonResponse(context)
        try:
            account_name = data_dict["account_name"]
        except KeyError as e:
            context = {"code": 1, "msg": "账户名不能为空"}
            return JsonResponse(context)
        try:
            account_login = data_dict["account_login"]
        except KeyError as e:
            context = {"code": 1, "msg": "账户登录名不能为空"}
            return JsonResponse(context)
        try:
            account_pin = data_dict["account_pin"]
        except KeyError as e:
            context = {"code": 1, "msg": "账户登录密码不能为空"}
            return JsonResponse(context)
        try:
            is_available = data_dict["is_available"]
        except KeyError as e:
            context = {"code": 1, "msg": "是否启用不能为空"}
            return JsonResponse(context)
        try:
            template = data_dict["template"]
        except KeyError as e:
            template = self.template
        try:
            script = data_dict["script"]
        except KeyError as e:
            script = self.script
        try:
            remark = data_dict["remark"]
        except KeyError as e:
            remark = self.remark
        if not all([id, account_id, account_name, account_login, account_pin]):
            context = {"code": 1, "msg": "参数不完整"}
            return JsonResponse(context)
        if not re.match(r"^[a-zA-Z0-9_]{4,16}$", str(account_id)):
            context = {"code": 1, "msg": "账户标识为4－16位的字母,数字或下划线"}
            return JsonResponse(context)
        try:
            account = Account.objects.get(id=id, account_user=user_id)
            account.account_id = account_id
            account.account_name = account_name
            account.account_login = account_login
            account.account_pin = account_pin
            account.template = template
            account.script = script
            account.remark = remark
            account.is_available = is_available
            account.account_user = user
            account.save()
        except Exception as e:
            context = {"code": 1, "msg": "数据库添加账户信息失败"}
            return JsonResponse(context)
        context = {"code": 0, "msg": "修改账户信息成功"}
        return JsonResponse(context)

    def delete(self, request):
        context = LoginRequiredMixin.login_required(request)
        if context["code"] != 0:
            return JsonResponse(context)
        user_id = context["user_id"]
        user = User.objects.get(id=user_id)
        id = request.GET.get("id")
        if not all([id]):
            context = {"code": 1, "msg": "参数不完整"}
            return JsonResponse(context)
        try:
            Account.objects.filter(id=id, account_user=user).delete()
        except Exception as e:
            context = {"code": 1, "msg": "删除账户信息失败"}
            return JsonResponse(context)
        context = {"code": 0, "msg": "删除账户信息成功"}
        return JsonResponse(context)


class AccountApi(View):
    def get(self, request):
        context = LoginRequiredMixin.login_required(request)
        if context["code"] != 0:
            return JsonResponse(context)
        user_id = context["user_id"]
        client_list = Account.objects.filter(account_user=user_id).order_by("id")
        if not client_list:
            context = {"code": 1, "msg": "还未有账户注册", "data": {}}
            return JsonResponse(context)
        all_account_data = list()
        for client in client_list:
            data_dict = dict()
            data_dict["id"] = client.id
            data_dict["account_name"] = client.account_name
            data_dict["account_id"] = client.account_id
            all_account_data.append(data_dict)
        data = {"all_data": all_account_data}
        context = {"code": 0, "msg": "获取账户api成功", "data": data}
        return JsonResponse(context, safe=False)
