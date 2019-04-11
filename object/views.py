from django.views.generic import View
from django.http import JsonResponse
from object.models import ObjectGroup, Object
from users.models import User
from util.commons import LoginRequiredMixin
from util import constants
import json
import re
import requests


class ObjectGroupView(View):
    def __init__(self):
        super(ObjectGroupView, self).__init__()
        self.template = ""
        self.script = ""
        self.remark = ""

    def get_single_data(self, id, user_id):
        obj_group = ObjectGroup.objects.filter(id=id, obj_group_user=user_id).first()
        obj_group_dict = dict()
        obj_group_dict["id"] = obj_group.id
        obj_group_dict["obj_group_id"] = obj_group.obj_group_id
        obj_group_dict["obj_group_name"] = obj_group.obj_group_name
        obj_group_dict["object_category"] = obj_group.object_category
        obj_group_dict["template"] = obj_group.template
        obj_group_dict["script"] = obj_group.script
        obj_group_dict["version"] = obj_group.version
        obj_group_dict["remark"] = obj_group.remark
        obj_group_dict["reference"] = obj_group.reference
        obj_group_dict["date_created"] = str(obj_group.date_created)[:-7]
        obj_group_dict["is_available"] = obj_group.is_available
        return obj_group_dict

    def get(self, request):
        context = LoginRequiredMixin.login_required(request)
        if context["code"] != 0:
            return JsonResponse(context)
        user_id = context["user_id"]
        obj_group_list = ObjectGroup.objects.filter(obj_group_user=user_id).order_by("id")
        if not obj_group_list:
            context = {"code": 0, "msg": "还未有对象组注册", "data": {"all_data": [], "single_data": {}}}
            return JsonResponse(context)
        id = request.GET.get("id")
        keyword = request.GET.get("keyword")
        if not keyword:
            if not id:
                id = obj_group_list[0].id
                all_obj_group_data_list = list()
                for obj_group in obj_group_list:
                    data_dict = dict()
                    data_dict["id"] = obj_group.id
                    data_dict["obj_group_id"] = obj_group.obj_group_id
                    data_dict["obj_group_name"] = obj_group.obj_group_name
                    all_obj_group_data_list.append(data_dict)
                obj_group_dict = self.get_single_data(id, user_id)
                data = {"all_data": all_obj_group_data_list, "single_data": obj_group_dict}
                context = {"code": 0, "msg": "获取对象组页面成功", "data": data}
                return JsonResponse(context)
            else:
                obj_group_dict = self.get_single_data(id, user_id)
                data = {"single_data": obj_group_dict}
                context = {"code": 0, "msg": "获取对象组页面成功", "data": data}
                return JsonResponse(context)
        else:
            keyword = keyword.strip(" ")
            search_result = list()
            for object_group in obj_group_list:
                object_group_dict = dict()
                if (keyword.upper() in object_group.obj_group_id.upper()) or (
                            keyword.upper() in object_group.obj_group_name.upper()):
                    object_group_dict["id"] = object_group.id
                    object_group_dict["obj_group_id"] = object_group.obj_group_id
                    object_group_dict["obj_group_name"] = object_group.obj_group_name
                if object_group.obj_group_name.upper() in keyword.upper():
                    object_group_dict["id"] = object_group.id
                    object_group_dict["obj_group_id"] = object_group.obj_group_id
                    object_group_dict["obj_group_name"] = object_group.obj_group_name
                if object_group_dict:
                    search_result.append(object_group_dict)
            if not search_result:
                data = {"all_data": search_result, "single_data": {}}
                context = {"code": 0, "msg": "搜索的内容不存在", "data": data}
                return JsonResponse(context)
            id = search_result[0]["id"]
            obj_group_dict = self.get_single_data(id, user_id)
            data = {"all_data": search_result, "single_data": obj_group_dict}
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
            obj_group_id = data_dict["obj_group_id"]
        except KeyError as e:
            context = {"code": 1, "msg": "分析对象组标识不能为空"}
            return JsonResponse(context)
        try:
            obj_group_name = data_dict["obj_group_name"]
        except KeyError as e:
            context = {"code": 1, "msg": "分析对象组名称不能为空"}
            return JsonResponse(context)
        try:
            object_category = data_dict["object_category"]
        except KeyError as e:
            context = {"code": 1, "msg": "分析对象组类型不能为空"}
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
        if not all([obj_group_id, obj_group_name, object_category]):
            context = {"code": 1, "msg": "参数不完整"}
            return JsonResponse(context)
        if not re.match(r"^[a-zA-Z0-9_]{4,16}", str(obj_group_id)):
            context = {"code": 1, "msg": "分析对象组标识必须为4-16位数字,字母或下划线"}
            return JsonResponse(context)
        try:
            tool = ObjectGroup.objects.get(obj_group_id=obj_group_id)
        except Exception as e:
            tool = False
        if tool:
            context = {"code": 1, "msg": "对象组标识已存在，请重新输入"}
            return JsonResponse(context)
        try:
            objectgroup = ObjectGroup()
            objectgroup.obj_group_id = obj_group_id
            objectgroup.obj_group_name = obj_group_name
            objectgroup.object_category = object_category
            objectgroup.template = template
            objectgroup.script = script
            objectgroup.remark = remark
            objectgroup.obj_group_user = user
            objectgroup.save()
        except Exception as e:
            context = {"code": 1, "msg": "数据库添加对象组失败"}
            return JsonResponse(context)
        context = {"code": 0, "msg": "添加对象组成功"}
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
            obj_group_id = data_dict["obj_group_id"]
        except KeyError as e:
            context = {"code": 1, "msg": "分析对象组标识不能为空"}
            return JsonResponse(context)
        try:
            obj_group_name = data_dict["obj_group_name"]
        except KeyError as e:
            context = {"code": 1, "msg": "分析对象组名称不能为空"}
            return JsonResponse(context)
        try:
            object_category = data_dict["object_category"]
        except KeyError as e:
            context = {"code": 1, "msg": "分析对象类型不能为空"}
            return JsonResponse(context)
        try:
            is_available = data_dict["is_available"]
        except KeyError as e:
            is_available = True 
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
        if not re.match(r"^[a-zA-Z0-9_]{4,16}", str(obj_group_id)):
            context = {"code": 1, "msg": "分析对象组标识必须为4-16位数字,字母或下划线"}
            return JsonResponse(context)
        try:
            objectgroup = ObjectGroup.objects.get(id=id, obj_group_user=user_id)
            objectgroup.obj_group_id = obj_group_id
            objectgroup.obj_group_name = obj_group_name
            objectgroup.object_category = object_category
            objectgroup.template = template
            objectgroup.script = script
            objectgroup.remark = remark
            objectgroup.is_available = is_available
            objectgroup.obj_group_user = user
            objectgroup.save()
        except Exception as e:
            context = {"code": 1, "msg": "数据库添加对象组失败"}
            return JsonResponse(context)
        context = {"code": 0, "msg": "修改对象组成功"}
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
        ObjectGroup.objects.filter(id=id, obj_group_user=user_id).delete()
        context = {"code": 0, "msg": "删除对象组成功"}
        return JsonResponse(context)


class ObjectsView(View):
    def __init__(self):
        super(ObjectsView, self).__init__()
        self.template = ""
        self.script = ""
        self.remark = ""

    def get_single_data(self, id, user_id):
        objects = Object.objects.filter(id=id, object_user=user_id).first()
        object_dict = dict()
        object_dict["id"] = objects.id
        object_dict["object_id"] = objects.object_id
        object_dict["object_reference_id"] = objects.object_reference_id
        object_dict["object_name"] = objects.object_name
        object_dict["object_model"] = objects.object_model
        object_dict["template"] = objects.template
        object_dict["script"] = objects.script
        object_dict["version"] = objects.version
        object_dict["remark"] = objects.remark
        object_dict["reference"] = objects.reference
        object_dict["date_created"] = str(objects.date_created)[:-7]
        object_dict["obj_group_id"] = objects.obj_group_id.obj_group_id
        object_dict["is_available"] = objects.is_available
        return object_dict

    def get(self, request):
        context = LoginRequiredMixin.login_required(request)
        if context["code"] != 0:
            return JsonResponse(context)
        user_id = context["user_id"]
        object_list = Object.objects.filter(object_user=user_id).order_by("id")
        if not object_list:
            context = {"code": 0, "msg": "还未有对象注册", "data": {"all_data": [], "single_data": {}}}
            return JsonResponse(context)
        id = request.GET.get("id")
        keyword = request.GET.get("keyword")
        if not keyword:
            if not id:
                id = object_list[0].id
                all_object_data = list()
                for object in object_list:
                    data_dict = dict()
                    data_dict["id"] = object.id
                    data_dict["object_id"] = object.object_id
                    data_dict["object_name"] = object.object_name
                    all_object_data.append(data_dict)
                object_dict = self.get_single_data(id, user_id)
                data = {"all_data": all_object_data, "single_data": object_dict}
                context = {"code": 0, "msg": "获取对象页面成功", "data": data}
                return JsonResponse(context)
            else:
                single_data = self.get_single_data(id, user_id)
                data = {"single_data": single_data}
                context = {"code": 0, "msg": "获取对象页面成功", "data": data}
                return JsonResponse(context)
        else:
            keyword = keyword.strip(" ")
            search_result = list()
            for object in object_list:
                object_dict = dict()
                if (keyword.upper() in object.object_id.upper()) or (keyword.upper() in object.object_name.upper()):
                    object_dict["id"] = object.id
                    object_dict["object_id"] = object.object_id
                    object_dict["object_name"] = object.object_name
                if object.object_name.upper() in keyword.upper():
                    object_dict["id"] = object.id
                    object_dict["object_id"] = object.object_id
                    object_dict["object_name"] = object.object_name
                if object_dict:
                    search_result.append(object_dict)
            if not search_result:
                data = {"all_data": search_result, "single_data": {}}
                context = {"code": 0, "msg": "搜索的内容不存在", "data": data}
                return JsonResponse(context)
            id = search_result[0]["id"]
            object_dict = self.get_single_data(id, user_id)
            data = {"all_data": search_result, "single_data": object_dict}
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
            object_id = data_dict["object_id"]
        except KeyError as e:
            context = {"code": 1, "msg": "分析对象标识不能为空"}
            return JsonResponse(context)
        object_id = str(object_id)
        try:
            is_available = data_dict["is_available"]
        except KeyError:
            is_available = True
        try:
            object_reference_id = data_dict["object_reference_id"]
        except KeyError as e:
            context = {"code": 1, "msg": "分析对象参考标识不能为空"}
            return JsonResponse(context)
        try:
            object_name = data_dict["object_name"]
        except KeyError as e:
            context = {"code": 1, "msg": "分析对象名不能为空"}
            return JsonResponse(context)
        try:
            obj_group_id = data_dict["obj_group_id"]
        except KeyError:
            context = {"code": 1, "msg": "分析对象组不能为空"}
            return JsonResponse(context)
        try:
            object_model = data_dict["object_model"]
        except KeyError:
            context = {"code": 1, "msg": "分析对象型号不能为空"}
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
        if not all([object_id, object_reference_id, object_name, object_model, obj_group_id]):
            context = {"code": 1, "msg": "参数不完整"}
            return JsonResponse(context)
        if not re.match(r"^[a-zA-Z0-9_]{4,16}", object_id):
            context = {"code": 1, "msg": "对象标识为4－16位的字母,数字或下划线"}
            return JsonResponse(context)
        try:
            tool = Object.objects.get(object_id=object_id)
        except Exception as e:
            tool = False
        if tool:
            context = {"code": 1, "msg": "分析对象已经在，请重新选择"}
            return JsonResponse(context)
        if not re.match(r"^[a-zA-Z0-9_]{4,16}", str(object_reference_id)):
            context = {"code": 1, "msg": "分析对象参考标识为4－16位的字母,数字或下划线"}
            return JsonResponse(context)
        try:
            group_id = ObjectGroup.objects.get(obj_group_id=obj_group_id)
        except KeyError as e:
            context = {"code": 1, "msg": "分析对象组错误，请重新填写"}
            return JsonResponse(context)
        try:
            objects = Object()
            objects.object_id = object_id
            objects.object_name = object_name
            objects.obj_group_id = group_id
            objects.object_reference_id = object_reference_id
            objects.object_model = object_model
            objects.is_available = is_available
            objects.script = script
            objects.remark = remark
            objects.template = template
            objects.object_user = user
            objects.save()
        except Exception:
            context = {"code": 1, "msg": "添加对象失败"}
            return JsonResponse(context)
        context = {"code": 0, "msg": "添加对象参数成功"}
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
            context = {"code": 1, "msg": "分析对象不存在！"}
            return JsonResponse(context)
        try:
            object_id = data_dict["object_id"]
        except KeyError as e:
            context = {"code": 1, "msg": "分析对象标识不能为空"}
            return JsonResponse(context)
        object_id = str(object_id)
        try:
            is_available = data_dict["is_available"]
        except KeyError:
            is_available = True
        try:
            object_reference_id = data_dict["object_reference_id"]
        except KeyError:
            context = {"code": 1, "msg": "分析对象参考标识不能为空"}
            return JsonResponse(context)
        try:
            object_name = data_dict["object_name"]
        except KeyError:
            context = {"code": 1, "msg": "分析对象名不能为空"}
            return JsonResponse(context)
        try:
            obj_group_id = data_dict["obj_group_id"]
        except KeyError:
            context = {"code": 1, "msg": "分析对象组不能为空"}
            return JsonResponse(context)
        try:
            object_model = data_dict["object_model"]
        except KeyError:
            context = {"code": 1, "msg": "分析对象型号不能为空"}
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
        if not re.match(r"^[a-zA-Z0-9_]{4,16}", str(object_id)):
            context = {"code": 1, "msg": "对象标识为4－16位的字母,数字或下划线"}
            return JsonResponse(context)
        if not re.match(r"^[a-zA-Z0-9_]{4,16}", str(object_reference_id)):
            context = {"code": 1, "msg": "分析对象参考标识为4－16位的字母,数字或下划线"}
            return JsonResponse(context)
        try:
            group_id = ObjectGroup.objects.get(obj_group_id=obj_group_id)
        except KeyError as e:
            context = {"code": 1, "msg": "分析对象组错误，请重新填写"}
            return JsonResponse(context)
        try:
            objects = Object.objects.get(id=id, object_user=user_id)
            objects.object_id = object_id
            objects.object_name = object_name
            objects.obj_group_id = group_id
            objects.object_reference_id = object_reference_id
            objects.object_model = object_model
            objects.script = script
            objects.remark = remark
            objects.template = template
            objects.is_available = is_available
            objects.object_user = user
            objects.save()
        except Exception:
            context = {"code": 1, "msg": "更新数据库失败"}
            return JsonResponse(context)
        context = {"code": 0, "msg": "修改对象成功"}
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
        Object.objects.filter(id=id, object_user=user_id).delete()
        context = {"code": 0, "msg": "删除对象信息成功"}
        return JsonResponse(context)


class ObjectApi(View):
    def get(self, request):
        context = LoginRequiredMixin.login_required(request)
        if context["code"] != 0:
            return JsonResponse(context)
        user_id = context["user_id"]
        object_list = Object.objects.filter(object_user=user_id).order_by("id")
        all_object_data_list = list()
        for objs in object_list:
            data_dict = dict()
            data_dict["id"] = objs.id
            data_dict["object_name"] = objs.object_name
            data_dict["object_id"] = objs.object_id
            all_object_data_list.append(data_dict)
        data = dict()
        data["all_data"] = all_object_data_list
        context = {"code": 0, "msg": "成功获取API", "data": data}
        return JsonResponse(context)


class GroupApi(View):
    def get(self, request):
        context = LoginRequiredMixin.login_required(request)
        if context["code"] != 0:
            return JsonResponse(context)
        user_id = context["user_id"]
        try:
            object_group_data = ObjectGroup.objects.filter(obj_group_user=user_id).order_by("id")
        except Exception as e:
            context = {"code": 1, "msg": "参数错误，请重新填写"}
            return JsonResponse(context)
        try:
            data_list = list()
            for group_data in object_group_data:
                data_dict = dict()
                data_dict["id"] = group_data.id
                data_dict["obj_group_name"] = group_data.obj_group_name
                data_dict["obj_group_id"] = group_data.obj_group_id
                data_list.append(data_dict)
            api_dict = dict()
            api_dict["all_data"] = data_list
            context = {"code": 0, "msg": "成功获取API", "data": api_dict}
            return JsonResponse(context, safe=False)
        except Exception as e:
            context = {"code": 1, "msg": "参数错误，请重新填写"}
            return JsonResponse(context)


class ApiqGetView(View):
    def __init__(self):
        super(ApiqGetView, self).__init__()
        self.login_url = constants.APIQ_LOGIN_URL
        self.apiq_url = constants.APIQ_INFO_URL

    def get(self, request):
        context = LoginRequiredMixin.login_required(request)
        if context["code"] != 0:
            return JsonResponse(context)
        param1 = {'username': 'admin', 'password': 'mix123456', 'system': 'PRO'}
        try:
            r1 = requests.post(self.login_url, data=param1)
            dic1 = json.loads(r1.text)
            token = dic1["data"]["token"]
            headers = {'Authorization': 'Bearer ' + token}
            data = {"is_all": 1, "page_index": 1, "page_size": 20, "condition": ""}
            result = requests.post(self.apiq_url, headers=headers, data=data)
            result = json.loads(result.text)
            all_data = list()
            for equipment in result["data"]:
                data = dict()
                data["object_id"] = equipment["equipment_id"]
                data["object_name"] = equipment["equipment_name"]
                all_data.append(data)
            all_data_dict = dict()
            all_data_dict["all_data"] = all_data
            return_data = {"code": 0, "msg": "The request is successful!", "data": all_data_dict}
        except Exception as e:
            return_data = {"code": 1, "msg": "request failed!"}
        return JsonResponse(return_data)


class ObjectInfo(View):
    def get(self, request):
        context = LoginRequiredMixin.login_required(request)
        if context["code"] != 0:
            return JsonResponse(context)
        user_id = context["user_id"]
        obj_group_id = request.GET.get("obj_group_id")
        if not obj_group_id:
            context = {"code": 1, "msg": "对象组id不能为空"}
            return JsonResponse(context)
        try:
            object_group = ObjectGroup.objects.get(obj_group_id=obj_group_id)
            id = object_group.id
            object_list = Object.objects.filter(obj_group_id=id, object_user=user_id).order_by("id")
        except Exception as e:
            context = {"code": 1, "msg": "相关对象信息不存在"}
            return JsonResponse(context)
        all_object_data = list()
        for obj in object_list:
            data_dict = dict()
            data_dict["id"] = obj.id
            data_dict["object_id"] = obj.object_id
            data_dict["object_name"] = obj.object_name
            all_object_data.append(data_dict)
        data = {"all_data": all_object_data}
        context = {"code": 0, "msg": "获取对象信息成功", "data": data}
        return JsonResponse(context)
