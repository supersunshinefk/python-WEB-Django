from django.http import JsonResponse
from django.views.generic.base import View
from users.models import User
from util.commons import LoginRequiredMixin
from .models import MessageOut
import json
import re
import ast


class MessageView(View):
    def __init__(self):
        super(MessageView, self).__init__()
        self.template = ""
        self.script = ""
        self.remark = ""

    def get_single_data(self, id, user_id):
        message = MessageOut.objects.filter(id=id, msg_out_user=user_id).first()
        message_dict = dict()
        message_dict["id"] = message.id
        message_dict["msg_out_id"] = message.msg_out_id
        message_dict["msg_out_name"] = message.msg_out_name
        message_dict["template"] = message.template
        message_dict["script"] = message.script
        message_dict["version"] = message.version
        message_dict["remark"] = message.remark
        message_dict["reference"] = message.reference
        message_dict["date_created"] = str(message.date_created)[:-7]
        message_dict["is_available"] = message.is_available
        return message_dict

    def get(self, request):
        context = LoginRequiredMixin.login_required(request)
        if context["code"] != 0:
            return JsonResponse(context)
        user_id = context["user_id"]
        id = request.GET.get('id')
        msg_out_list = MessageOut.objects.filter(msg_out_user=user_id).order_by("id")
        if not msg_out_list:
            context = {"code": 0, "msg": "还未有消息提示注册", "data": {"all_data": [], "single_data": {}}}
            return JsonResponse(context)
        keyword = request.GET.get("keyword")
        if not keyword:
            if not id:
                id = msg_out_list[0].id
                all_msg_data = list()
                for msg in msg_out_list:
                    data_dict = dict()
                    data_dict["id"] = msg.id
                    data_dict["msg_out_id"] = msg.msg_out_id
                    data_dict["msg_out_name"] = msg.msg_out_name
                    all_msg_data.append(data_dict)
                message_dict = self.get_single_data(id, user_id)
                data = {"all_data": all_msg_data, "single_data": message_dict}
                context = {"code": "0", "msg": "获取消息提示成功", "data": data}
                return JsonResponse(context)
            else:
                message_dict = self.get_single_data(id, user_id)
                data = {"single_data": message_dict}
                context = {"code": "0", "msg": "获取消息提示成功", "data": data}
                return JsonResponse(context)
        else:
            keyword = keyword.strip(" ")
            search_result = list()
            for message in msg_out_list:
                message_dict = dict()
                if (keyword.upper() in message.msg_out_id.upper()) or (keyword.upper() in message.msg_out_name.upper()):
                    message_dict["id"] = message.id
                    message_dict["msg_out_id"] = message.msg_out_id
                    message_dict["msg_out_name"] = message.msg_out_name
                if message.msg_out_name.upper() in keyword.upper():
                    message_dict["id"] = message.id
                    message_dict["msg_out_id"] = message.msg_out_id
                    message_dict["msg_out_name"] = message.msg_out_name
                if message_dict:
                    search_result.append(message_dict)
            if not search_result:
                data = {"all_data": search_result, "single_data": {}}
                context = {"code": 0, "msg": "搜索的内容不存在", "data": data}
                return JsonResponse(context)
            id = search_result[0]["id"]
            message_dict = self.get_single_data(id, user_id)
            data = {"all_data": search_result, "single_data": message_dict}
            context = {"code": 0, "msg": "搜索成功", "data": data}
            return JsonResponse(context)

    def post(self, request):
        context = LoginRequiredMixin.login_required(request)
        if context["code"] != 0:
            return JsonResponse(context)
        user_id = context["user_id"]
        user = User.objects.get(id=user_id)
        try:
            post_data = json.loads(request.body.decode("utf-8"))
        except Exception as e:
            context = {"code": 1, "msg": "获取json数据失败"}
            return JsonResponse(context)
        try:
            msg_out_id = post_data["msg_out_id"]
        except KeyError as e:
            context = {"code": 1, "msg": "消息提示标识不能为空"}
            return JsonResponse(context)
        try:
            msg_out_name = post_data["msg_out_name"]
        except KeyError as e:
            context = {"code": 1, "msg": "消息提示名称不能为空"}
            return JsonResponse(context)
        try:
            template = post_data["template"]
        except KeyError as e:
            template = self.template
        try:
            script = post_data["script"]
        except KeyError as e:
            script = self.script
        try:
            remark = post_data["remark"]
        except KeyError as e:
            remark = self.remark
        if not all([msg_out_id, msg_out_name]):
            context = {"code": 1, "msg": "参数不完整"}
            return JsonResponse(context)
        try:
            message = MessageOut.objects.get(msg_out_id=msg_out_id)
        except Exception as e:
            message = False
        if message:
            context = {"code": 1, "msg": "消息提示标识已存在，请重新输入！"}
            return JsonResponse(context)
        if not re.match(r"^[a-zA-Z0-9_]{4,16}$", str(msg_out_id)):
            context = {"code": 1, "msg": "消息提示标识为4－16位的字母,数字或下划线"}
            return JsonResponse(context)
        if script:
            try:
                new_script = json.loads(script)
            except Exception as e:
                msg = "Json script error," + "%s" % e
                context = {"code": 1, "msg": msg}
                return JsonResponse(context)
        try:
            messageout = MessageOut()
            messageout.msg_out_id = msg_out_id
            messageout.msg_out_name = msg_out_name
            messageout.script = script
            messageout.template = template
            messageout.remark = remark
            messageout.msg_out_user = user
            messageout.save()
        except Exception as e:
            context = {"code": 1, "msg": "创建消息提示失败"}
            return JsonResponse(context)
        context = {"code": "0", "msg": "消息提示创建成功"}
        return JsonResponse(context)

    def delete(self, request):
        context = LoginRequiredMixin.login_required(request)
        if context["code"] != 0:
            return JsonResponse(context)
        user_id = context["user_id"]
        id = request.GET.get("id")
        if not all([id]):
            context = {"code": 1, "msg": "参数不完整"}
            return JsonResponse(context)
        try:
            MessageOut.objects.filter(id=id, msg_out_user=user_id).delete()
        except Exception as e:
            context = {"code": 1, "msg": "删除信息提示失败"}
            return JsonResponse(context)
        context = {"code": 0, "msg": "删除信息提示成功"}
        return JsonResponse(context)

    def put(self, request):
        context = LoginRequiredMixin.login_required(request)
        if context["code"] != 0:
            return JsonResponse(context)
        user_id = context["user_id"]
        user = User.objects.get(id=user_id)
        try:
            put_data = json.loads(request.body.decode("utf-8"))
        except Exception as e:
            context = {"code": 1, "msg": "获取json数据失败"}
            return JsonResponse(context)
        try:
            id = put_data['id']
        except KeyError as e:
            context = {"code": 1, "msg": "id不能为空"}
            return JsonResponse(context)
        try:
            msg_out_id = put_data["msg_out_id"]
        except KeyError as e:
            context = {"code": 1, "msg": "消息提示标识不能为空"}
            return JsonResponse(context)
        try:
            msg_out_name = put_data["msg_out_name"]
        except KeyError as e:
            context = {"code": 1, "msg": "消息提示名称不能为空"}
            return JsonResponse(context)
        try:
            is_available = put_data["is_available"]
        except KeyError as e:
            context = {"code": 1, "msg": "是否启用不能为空"}
            return JsonResponse(context)
        try:
            template = put_data["template"]
        except KeyError as e:
            template = self.template
        try:
            script = put_data["script"]
        except KeyError as e:
            script = self.script
        try:
            remark = put_data["remark"]
        except KeyError as e:
            remark = self.remark
        if not all([id, msg_out_id, msg_out_name]):
            context = {"code": 1, "msg": "参数不完整"}
            return JsonResponse(context)
        if not re.match(r"^[a-zA-Z0-9_]{4,16}$", str(msg_out_id)):
            context = {"code": 1, "msg": "消息提示标识为4－16位的字母,数字或下划线"}
            return JsonResponse(context)
        if script:
            try:
                new_script = json.loads(script)
            except Exception as e:
                msg = "Json script error," + "%s" % e
                context = {"code": 1, "msg": msg}
                return JsonResponse(context)
        try:
            messageout = MessageOut.objects.get(id=id, msg_out_user=user_id)
            messageout.msg_out_id = msg_out_id
            messageout.msg_out_name = msg_out_name
            messageout.script = script
            messageout.template = template
            messageout.remark = remark
            messageout.is_available = is_available
            messageout.msg_out_user = user
            messageout.save()
        except Exception as e:
            context = {"code": 1, "msg": "修改消息消息提示失败"}
            return JsonResponse(context)
        context = {"code": "0", "msg": "修改消息提示成功"}
        return JsonResponse(context)


class MessageApi(View):
    def get(self, request):
        context = LoginRequiredMixin.login_required(request)
        if context["code"] != 0:
            return JsonResponse(context)
        user_id = context["user_id"]
        msg_out = MessageOut.objects.filter(msg_out_user=user_id).order_by("id")
        all_msg_data = list()
        for msg in msg_out:
            data_dict = dict()
            data_dict["id"] = msg.id
            data_dict["msg_out_id"] = msg.msg_out_id
            data_dict["msg_out_name"] = msg.msg_out_name
            all_msg_data.append(data_dict)
        data = {"all_data": all_msg_data}
        context = {"code": 0, "msg": "获取数据管道api成功", "data": data}
        return JsonResponse(context)
