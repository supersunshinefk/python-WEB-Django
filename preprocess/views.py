from django.http import JsonResponse
from django.views.generic.base import View
from users.models import User
from util.commons import LoginRequiredMixin, OrganizerScriptVerify, FilterScriptVerify
from .models import DataFilter, DataOrganizer
import json
import re
import ast


class FilterView(View):
    def __init__(self):
        super(FilterView, self).__init__()
        self.template = ""
        self.remark = ""
        self.reference = ""

    def get_single_data(self, id, user_id):
        filter = DataFilter.objects.filter(id=id, filter_user=user_id).first()
        filter_dict = dict()
        filter_dict["id"] = filter.id
        filter_dict["filter_id"] = filter.filter_id
        filter_dict["filter_name"] = filter.filter_name
        filter_dict["template"] = filter.template
        filter_dict["script"] = filter.script
        filter_dict["version"] = filter.version
        filter_dict["remark"] = filter.remark
        filter_dict["reference"] = filter.reference
        filter_dict["date_created"] = str(filter.date_created)[:-7]
        filter_dict["is_available"] = filter.is_available
        return filter_dict

    def get(self, request):
        context = LoginRequiredMixin.login_required(request)
        if context["code"] != 0:
            return JsonResponse(context)
        user_id = context["user_id"]
        filter_list = DataFilter.objects.filter(filter_user=user_id).order_by("id")
        if not filter_list:
            context = {"code": 0, "msg": "还未有过滤器注册",
                       "data": {"all_data": [], "single_data": {}}}
            return JsonResponse(context)
        id = request.GET.get('id')
        keyword = request.GET.get("keyword")
        if not keyword:
            if not id:
                id = filter_list[0].id
                all_filter_data = list()
                for filter in filter_list:
                    data_dict = dict()
                    data_dict["id"] = filter.id
                    data_dict["filter_id"] = filter.filter_id
                    data_dict["filter_name"] = filter.filter_name
                    all_filter_data.append(data_dict)
                filter_dict = self.get_single_data(id, user_id)
                data = {"all_data": all_filter_data, "single_data": filter_dict}
                context = {"code": "0", "msg": "获取过滤器成功", "data": data}
                return JsonResponse(context)
            else:
                filter_dict = self.get_single_data(id, user_id)
                data = {"single_data": filter_dict}
                context = {"code": "0", "msg": "获取过滤器成功", "data": data}
                return JsonResponse(context)
        else:
            keyword = keyword.strip(" ")
            search_result = list()
            for filter in filter_list:
                filter_dict = dict()
                if (keyword.upper() in filter.filter_id.upper()) or (keyword.upper() in filter.filter_name.upper()):
                    filter_dict["id"] = filter.id
                    filter_dict["filter_id"] = filter.filter_id
                    filter_dict["filter_name"] = filter.filter_name
                if filter.filter_name.upper() in keyword.upper():
                    filter_dict["id"] = filter.id
                    filter_dict["filter_id"] = filter.filter_id
                    filter_dict["filter_name"] = filter.filter_name
                if filter_dict:
                    search_result.append(filter_dict)
            if not search_result:
                data = {"all_data": search_result, "single_data": {}}
                context = {"code": 0, "msg": "搜索的内容不存在", "data": data}
                return JsonResponse(context)
            id = search_result[0]["id"]
            filter_dict = self.get_single_data(id, user_id)
            data = {"all_data": search_result, "single_data": filter_dict}
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
            filter_id = post_data["filter_id"]
        except KeyError as e:
            context = {"code": 1, "msg": "过滤器标识不能为空"}
            return JsonResponse(context)
        try:
            filter_name = post_data["filter_name"]
        except KeyError as e:
            context = {"code": 1, "msg": "过滤器名称不能为空"}
            return JsonResponse(context)
        try:
            script = post_data["script"]
            if not script:

                context = {"code": 1, "msg": "脚本不能为空"}
                return JsonResponse(context)
        except KeyError as e:
            context = {"code": 1, "msg": "脚本不能为空"}
            return JsonResponse(context)
        try:
            template = post_data["template"]
        except KeyError as e:
            template = self.template
        try:
            remark = post_data["remark"]
        except KeyError as e:
            remark = self.remark
        if not re.match(r"^[u4e00-u9fa5·0-9A-z]+$", str(filter_id)):
            context = {"code": 1, "msg": "过滤器标识不能有中文"}
            return JsonResponse(context)
        try:
            filter_object = DataFilter.objects.get(filter_id=filter_id)
        except Exception as e:
            filter_object = False
        if filter_object:
            context = {"code": 1, "msg": "过滤器标识已存在，请重新输入！"}
            return JsonResponse(context)
        try:
            new_script = json.loads(script)
        except Exception as e:
            msg = "脚本Json格式错误"
            context = {"code": 1, "msg": msg}
            return JsonResponse(context)
        context = FilterScriptVerify.script_verify(new_script)
        if context["code"] != 0:
            return JsonResponse(context)
        try:
            datafilter = DataFilter()
            datafilter.filter_id = filter_id
            datafilter.filter_name = filter_name
            datafilter.script = script
            datafilter.template = template
            datafilter.remark = remark
            datafilter.filter_user = user
            datafilter.save()
        except Exception as e:
            context = {"code": 1, "msg": "创建过滤器信息失败"}
            return JsonResponse(context)
        context = {"code": "0", "msg": "创建过滤器成功"}
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
            DataFilter.objects.filter(id=id, filter_user=user_id).delete()
        except Exception as e:
            context = {"code": 1, "msg": "删除过滤器失败"}
            return JsonResponse(context)
        context = {"code": 0, "msg": "删除过滤器成功"}
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
            id = put_data["id"]
        except KeyError as e:
            context = {"code": 1, "msg": "数据错误，请刷新重试"}
            return JsonResponse(context)
        try:
            filter_id = put_data["filter_id"]
        except KeyError as e:
            context = {"code": 1, "msg": "过滤器标识不能为空"}
            return JsonResponse(context)
        try:
            filter_name = put_data["filter_name"]
        except KeyError as e:
            context = {"code": 1, "msg": "过滤器名称不能为空"}
            return JsonResponse(context)
        try:
            script = put_data["script"]
            if not script:
                context = {"code": 1, "msg": "脚本不能为空"}
                return JsonResponse(context)
        except KeyError as e:
            context = {"code": 1, "msg": "脚本不能为空"}
            return JsonResponse(context)
        try:
            is_available = put_data["is_available"]
        except KeyError as e:
            is_available = True
        try:
            template = put_data["template"]
        except KeyError as e:
            template = self.template
        try:
            remark = put_data["remark"]
        except KeyError as e:
            remark = self.remark
        if not re.match(r"^[a-zA-Z0-9_]{4,16}$", str(filter_id)):
            context = {"code": 1, "msg": "过滤器标识为4－16位的字母,数字或下划线"}
            return JsonResponse(context)
        try:
            new_script = json.loads(script)
        except Exception as e:
            msg = "脚本Json格式错误"
            context = {"code": 1, "msg": msg}
            return JsonResponse(context)
        context = FilterScriptVerify.script_verify(new_script)
        if context["code"] != 0:
            return JsonResponse(context)
        try:
            datafilter = DataFilter.objects.get(id=id, filter_user=user_id)
            datafilter.filter_id = filter_id
            datafilter.filter_name = filter_name
            datafilter.script = script
            datafilter.template = template
            datafilter.remark = remark
            datafilter.is_available = is_available
            datafilter.filter_user = user
            datafilter.save()
        except Exception as e:
            context = {"code": 1, "msg": "修改过滤器失败"}
            return JsonResponse(context)
        context = {"code": "0", "msg": "修改过滤器成功"}
        return JsonResponse(context)


class OrganizerView(View):
    def __init__(self):
        super(OrganizerView, self).__init__()
        self.template = ""
        self.remark = ""
        self.reference = ""

    def get_single_data(self, id, user_id):
        organizer = DataOrganizer.objects.filter(id=id, organizer_user=user_id).first()
        organizer_dict = dict()
        organizer_dict["id"] = organizer.id
        organizer_dict["organizer_id"] = organizer.organizer_id
        organizer_dict["organizer_name"] = organizer.organizer_name
        organizer_dict["template"] = organizer.template
        organizer_dict["script"] = organizer.script
        organizer_dict["version"] = organizer.version
        organizer_dict["remark"] = organizer.remark
        organizer_dict["reference"] = organizer.reference
        organizer_dict["date_created"] = str(organizer.date_created)[:19]
        organizer_dict["is_available"] = organizer.is_available
        return organizer_dict

    def get(self, request):
        context = LoginRequiredMixin.login_required(request)
        if context["code"] != 0:
            return JsonResponse(context)
        user_id = context["user_id"]
        organizer_list = DataOrganizer.objects.filter(organizer_user=user_id).order_by("id")
        if not organizer_list:
            context = {"code": 0, "msg": "还未有组织器注册", "data": {"all_data": [], "single_data": {}}}
            return JsonResponse(context)
        id = request.GET.get('id')
        keyword = request.GET.get("keyword")
        if not keyword:
            if not id:
                id = organizer_list[0].id
                all_organizer_data = list()
                for organizer in organizer_list:
                    data_dict = dict()
                    data_dict["id"] = organizer.id
                    data_dict["organizer_id"] = organizer.organizer_id
                    data_dict["organizer_name"] = organizer.organizer_name
                    all_organizer_data.append(data_dict)
                organizer_dict = self.get_single_data(id, user_id)
                data = {"all_data": all_organizer_data, "single_data": organizer_dict}
                context = {"code": "0", "msg": "获取组织器成功", "data": data}
                return JsonResponse(context)
            else:
                organizer_dict = self.get_single_data(id, user_id)
                data = {"single_data": organizer_dict}
                context = {"code": "0", "msg": "获取组织器成功", "data": data}
                return JsonResponse(context)
        else:
            keyword = keyword.strip(" ")
            search_result = list()
            for organizer in organizer_list:
                organizer_dict = dict()
                if (keyword.upper() in organizer.organizer_id.upper()) or (
                            keyword.upper() in organizer.organizer_name.upper()):
                    organizer_dict["id"] = organizer.id
                    organizer_dict["organizer_id"] = organizer.organizer_id
                    organizer_dict["organizer_name"] = organizer.organizer_name
                if organizer.organizer_name.upper() in keyword.upper():
                    organizer_dict["id"] = organizer.id
                    organizer_dict["organizer_id"] = organizer.organizer_id
                    organizer_dict["organizer_name"] = organizer.organizer_name
                if organizer_dict:
                    search_result.append(organizer_dict)
            if not search_result:
                data = {"all_data": search_result, "single_data": {}}
                context = {"code": 0, "msg": "搜索的内容不存在", "data": data}
                return JsonResponse(context)
            id = search_result[0]["id"]
            organizer_dict = self.get_single_data(id, user_id)
            data = {"all_data": search_result, "single_data": organizer_dict}
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
            organizer_id = post_data["organizer_id"]
        except KeyError as e:
            context = {"code": 1, "msg": "组织器标识不能为空"}
            return JsonResponse(context)
        try:
            organizer_name = post_data["organizer_name"]
        except KeyError as e:
            context = {"code": 1, "msg": "组织器名称不能为空"}
            return JsonResponse(context)
        try:
            script = post_data["script"]
            if not script:
                context = {"code": 1, "msg": "脚本不能为空"}
                return JsonResponse(context)
        except KeyError as e:
            context = {"code": 1, "msg": "脚本不能为空"}
            return JsonResponse(context)
        try:
            template = post_data["template"]
        except KeyError as e:
            template = self.template
        try:
            remark = post_data["remark"]
        except KeyError as e:
            remark = self.remark
        if not all([organizer_id, organizer_name, script]):
            context = {"code": 1, "msg": "参数不完整"}
            return JsonResponse(context)
        if not re.match(r"^[a-zA-Z0-9_]{4,16}$", str(organizer_id)):
            context = {"code": 1, "msg": "组织器标识为4－16位的字母,数字或下划线"}
            return JsonResponse(context)
        try:
            organizer_object = DataOrganizer.objects.get(organizer_id=organizer_id)
        except Exception as e:
            organizer_object = False
        if organizer_object:
            context = {"code": 1, "msg": "组织器标识已存在，请重新输入！"}
            return JsonResponse(context)
        try:
            new_script = json.loads(script)
        except Exception as e:
            msg = "脚本Json格式错误"
            context = {"code": 1, "msg": msg}
            return JsonResponse(context)
        context = OrganizerScriptVerify.script_verify(new_script)
        if context["code"] != 0:
            return JsonResponse(context)
        try:
            dataorganizer = DataOrganizer()
            dataorganizer.organizer_id = organizer_id
            dataorganizer.organizer_name = organizer_name
            dataorganizer.script = script
            dataorganizer.template = template
            dataorganizer.remark = remark
            dataorganizer.organizer_user = user
            dataorganizer.save()
        except Exception as e:
            context = {"code": 1, "msg": "创建组织器失败"}
            return JsonResponse(context)
        context = {"code": "0", "msg": "创建组织器成功"}
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
            DataOrganizer.objects.filter(id=id, organizer_user=user_id).delete()
        except Exception as e:
            context = {"code": 1, "msg": "删除组织器失败"}
            return JsonResponse(context)
        context = {"code": 0, "msg": "删除组织器成功"}
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
            id = put_data["id"]
        except KeyError as e:
            context = {"code": 1, "msg": "数据获取失败，请刷新重试"}
            return JsonResponse(context)
        try:
            organizer_id = put_data["organizer_id"]
        except KeyError as e:
            context = {"code": 1, "msg": "组织器标识不能为空"}
            return JsonResponse(context)
        try:
            organizer_name = put_data["organizer_name"]
        except KeyError as e:
            context = {"code": 1, "msg": "组织器标识不能为空"}
            return JsonResponse(context)
        try:
            script = put_data["script"]
            if not script:
                context = {"code": 1, "msg": "脚本不能为空"}
                return JsonResponse(context)
        except KeyError as e:
            context = {"code": 1, "msg": "脚本不能为空"}
            return JsonResponse(context)
        try:
            is_available = put_data["is_available"]
        except KeyError as e:
            is_available = True
        try:
            template = put_data["template"]
        except KeyError as e:
            template = self.template
        try:
            remark = put_data["remark"]
        except KeyError as e:
            remark = self.remark
        if not re.match(r"^[a-zA-Z0-9_]{4,16}$", str(organizer_id)):
            context = {"code": 1, "msg": "组织器标识为4－16位的字母,数字或下划线"}
            return JsonResponse(context)
        try:
            new_script = json.loads(script)
        except Exception as e:
            msg = "脚本Json格式错误"
            context = {"code": 1, "msg": msg}
            return JsonResponse(context)
        context = OrganizerScriptVerify.script_verify(new_script)
        if context["code"] != 0:
            return JsonResponse(context)
        try:
            dataorganizer = DataOrganizer.objects.get(id=id, organizer_user=user_id)
            dataorganizer.organizer_id = organizer_id
            dataorganizer.organizer_name = organizer_name
            dataorganizer.script = script
            dataorganizer.template = template
            dataorganizer.remark = remark
            dataorganizer.is_available = is_available
            dataorganizer.organizer_user = user
            dataorganizer.save()
        except Exception as e:
            context = {"code": 1, "msg": "修改组织器失败"}
            return JsonResponse(context)
        context = {"code": "0", "msg": "修改组织器成功"}
        return JsonResponse(context)


class FilterApi(View):
    def get(self, request):
        context = LoginRequiredMixin.login_required(request)
        if context["code"] != 0:
            return JsonResponse(context)
        user_id = context["user_id"]
        filter_list = DataFilter.objects.filter(filter_user=user_id).order_by("id")
        all_filter_data = list()
        for filter in filter_list:
            data_dict = dict()
            data_dict["id"] = filter.id
            data_dict["filter_name"] = filter.filter_name
            data_dict["filter_id"] = filter.filter_id
            all_filter_data.append(data_dict)
        data = {"all_data": all_filter_data}
        context = {"code": 0, "msg": "获取过滤器api成功", "data": data}
        return JsonResponse(context, safe=False)


class OrganizerApi(View):
    def get(self, request):
        context = LoginRequiredMixin.login_required(request)
        if context["code"] != 0:
            return JsonResponse(context)
        user_id = context["user_id"]
        organzier_list = DataOrganizer.objects.filter(organizer_user=user_id).order_by("id")
        all_organizer_data = list()
        for organizer in organzier_list:
            data_dict = dict()
            data_dict["id"] = organizer.id
            data_dict["organizer_name"] = organizer.organizer_name
            data_dict["organizer_id"] = organizer.organizer_id
            all_organizer_data.append(data_dict)
        data = {"all_data": all_organizer_data}
        context = {"code": 0, "msg": "获取组织器api成功", "data": data}
        return JsonResponse(context, safe=False)

