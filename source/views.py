from django.views.generic import View
from django.http import JsonResponse
from source.models import DataSource, DataPipe
from util.commons import LoginRequiredMixin
from users.models import User
import json
import re


class SourceView(View):
    def __init__(self):
        super(SourceView, self).__init__()
        self.template = ""
        self.script = ""
        self.remark = ""

    def get_single_data(self, id, user_id):
        source = DataSource.objects.filter(id=id, source_user=user_id).first()
        source_dict = dict()
        source_dict["id"] = source.id
        source_dict["source_id"] = source.source_id
        source_dict["source_name"] = source.source_name
        source_dict["source_mode"] = source.source_mode
        source_dict["template"] = source.template
        source_dict["script"] = source.script
        source_dict["version"] = source.version
        source_dict["remark"] = source.remark
        source_dict["reference"] = source.reference
        source_dict["date_created"] = str(source.date_created)[:19]
        source_dict["is_available"] = source.is_available
        return source_dict

    def get(self, request):
        context = LoginRequiredMixin.login_required(request)
        if context["code"] != 0:
            return JsonResponse(context)
        user_id = context["user_id"]
        data_source_list = DataSource.objects.filter(source_user=user_id).order_by("id")
        if not data_source_list:
            context = {"code": 0, "msg": "还未有数据源注册", "data": {"all_data": [], "single_data": {}}}
            return JsonResponse(context)
        id = request.GET.get("id")
        keyword = request.GET.get("keyword")
        if not keyword:
            if not id:
                id = data_source_list[0].id
                all_data_source_list = list()
                for source in data_source_list:
                    data_dict = dict()
                    data_dict["id"] = source.id
                    data_dict["source_id"] = source.source_id
                    data_dict["source_name"] = source.source_name
                    all_data_source_list.append(data_dict)
                source_dict = self.get_single_data(id, user_id)
                data = {"all_data": all_data_source_list, "single_data": source_dict}
                context = {"code": 0, "msg": "获取数据源页面成功", "data": data}
                return JsonResponse(context)
            else:
                source_dict = self.get_single_data(id, user_id)
                data = {"single_data": source_dict}
                context = {"code": 0, "msg": "获取数据源页面成功", "data": data}
                return JsonResponse(context)
        else:
            keyword = keyword.strip(" ")
            search_result = list()
            for source in data_source_list:
                source_dict = dict()
                if (keyword.upper() in source.source_id.upper()) or (keyword.upper() in source.source_name.upper()):
                    source_dict["id"] = source.id
                    source_dict["source_id"] = source.source_id
                    source_dict["source_name"] = source.source_name
                if source.source_name.upper() in keyword.upper():
                    source_dict["id"] = source.id
                    source_dict["source_id"] = source.source_id
                    source_dict["source_name"] = source.source_name
                if source_dict:
                    search_result.append(source_dict)
            if not search_result:
                data = {"all_data": search_result, "single_data": {}}
                context = {"code": 0, "msg": "搜索的内容不存在", "data": data}
                return JsonResponse(context)
            id = search_result[0]["id"]
            source_dict = self.get_single_data(id, user_id)
            data = {"all_data": search_result, "single_data": source_dict}
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
            source_id = data_dict["source_id"]
        except KeyError as e:
            context = {"code": 1, "msg": "数据源标识不能为空"}
            return JsonResponse(context)
        try:
            source_name = data_dict["source_name"]
        except KeyError as e:
            context = {"code": 1, "msg": "数据源名称不能为空"}
            return JsonResponse(context)
        try:
            source_mode = data_dict["source_mode"]
        except KeyError as e:
            context = {"code": 1, "msg": "数据源模式不能为空"}
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
        try:
            tool = DataSource.objects.get(source_id=source_id)
        except Exception as e:
            tool = False
        if tool:
            context = {"code": 1, "msg": "数据源标识已存在，请重新输入"}
            return JsonResponse(context)
        if not re.match(r"^[a-zA-Z0-9_]{4,16}$", str(source_id)):
            context = {"code": 1, "msg": "数据源标识为4－16位的字母,数字或下划线"}
            return JsonResponse(context)
        try:
            datasource = DataSource()
            datasource.source_id = source_id
            datasource.source_name = source_name
            datasource.template = template
            datasource.script = script
            datasource.remark = remark
            datasource.source_mode = source_mode
            datasource.source_user = user
            datasource.save()
        except Exception as e:
            context = {"code": 1, "msg": "添加数据源失败"}
            return JsonResponse(context)
        context = {"code": 0, "msg": "添加数据源成功"}
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
            context = {"code": 1, "msg": "获取数据失败，请刷新重试"}
            return JsonResponse(context)
        try:
            source_id = data_dict["source_id"]
        except KeyError as e:
            context = {"code": 1, "msg": "数据源标识不能为空"}
            return JsonResponse(context)
        try:
            source_name = data_dict["source_name"]
        except KeyError as e:
            context = {"code": 1, "msg": "数据源名称不能为空"}
            return JsonResponse(context)
        try:
            is_available = data_dict["is_available"]
        except KeyError as e:
            is_available = True
        try:
            source_mode = data_dict["source_mode"]
        except KeyError as e:
            context = {"code": 1, "msg": "数据源模式不能为空"}
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
        if not re.match(r"^[a-zA-Z0-9_]{4,16}$", str(source_id)):
            context = {"code": 1, "msg": "数据源标识为4－16位的字母,数字或下划线"}
            return JsonResponse(context)
        try:
            datasource = DataSource.objects.get(id=id, source_user=user_id)
            datasource.template = template
            datasource.script = script
            datasource.remark = remark
            datasource.is_available = is_available
            datasource.source_mode = source_mode
            datasource.source_user = user
            datasource.save()
        except Exception as e:
            context = {"code": 1, "msg": "修改数据源失败"}
            return JsonResponse(context)
        context = {"code": 0, "msg": "修改数据源成功"}
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
            DataSource.objects.filter(id=id, source_user=user_id).delete()
        except Exception as e:
            context = {"code": 1, "msg": "删除数据源失败"}
            return JsonResponse(context)
        context = {"code": 0, "msg": "删除数据源成功"}
        return JsonResponse(context)


class PipeView(View):
    def __init__(self):
        super(PipeView, self).__init__()
        self.template = ""
        self.script = ""
        self.remark = ""

    def get_single_data(self, id, user_id):
        pipe = DataPipe.objects.filter(id=id, pipe_user=user_id).first()
        pipe_dict = dict()
        pipe_dict["id"] = pipe.id
        pipe_dict["pipe_id"] = pipe.pipe_id
        pipe_dict["pipe_name"] = pipe.pipe_name
        pipe_dict["template"] = pipe.template
        pipe_dict["script"] = pipe.script
        pipe_dict["version"] = pipe.version
        pipe_dict["remark"] = pipe.remark
        pipe_dict["reference"] = pipe.reference
        pipe_dict["date_created"] = str(pipe.date_created)[:-7]
        pipe_dict["is_available"] = pipe.is_available
        return pipe_dict

    def get(self, request):
        context = LoginRequiredMixin.login_required(request)
        if context["code"] != 0:
            return JsonResponse(context)
        user_id = context["user_id"]
        data_pipe_list = DataPipe.objects.filter(pipe_user=user_id).order_by("id")
        if not data_pipe_list:
            context = {"code": 0, "msg": "还未有数据管道注册", 
                    "data": {"all_data": [], "single_data": {}}}
            return JsonResponse(context)
        id = request.GET.get("id")
        keyword = request.GET.get("keyword")
        if not keyword:
            if not id:
                id = data_pipe_list[0].id
                all_data_pipe_list = list()
                for pipe in data_pipe_list:
                    data_dict = dict()
                    data_dict["id"] = pipe.id
                    data_dict["pipe_id"] = pipe.pipe_id
                    data_dict["pipe_name"] = pipe.pipe_name
                    all_data_pipe_list.append(data_dict)
                pipe_dict = self.get_single_data(id, user_id)
                data = {"all_data": all_data_pipe_list, "single_data": pipe_dict}
                context = {"code": 0, "msg": "获取数据管道页面成功", 
                        "data": data}
                return JsonResponse(context)
            else:
                pipe_dict = self.get_single_data(id, user_id)
                data = {"single_data": pipe_dict}
                context = {"code": 0, "msg": "获取数据管道页面成功", "data": data}
                return JsonResponse(context)
        else:
            keyword = keyword.strip(" ")
            search_result = list()
            for pipe in data_pipe_list:
                pipe_dict = dict()
                if (keyword.upper() in pipe.pipe_id.upper()) or (keyword.upper() in pipe.pipe_name.upper()):
                    pipe_dict["id"] = pipe.id
                    pipe_dict["pipe_id"] = pipe.pipe_id
                    pipe_dict["pipe_name"] = pipe.pipe_name
                if pipe.pipe_name.upper() in keyword.upper():
                    pipe_dict["id"] = pipe.id
                    pipe_dict["pipe_id"] = pipe.pipe_id
                    pipe_dict["pipe_name"] = pipe.pipe_name
                if pipe_dict:
                    search_result.append(pipe_dict)
            if not search_result:
                data = {"all_data": search_result, "single_data": {}}
                context = {"code": 0, "msg": "搜索的内容不存在", "data": data}
                return JsonResponse(context)
            id = search_result[0]["id"]
            pipe_dict = self.get_single_data(id, user_id)
            data = {"all_data": search_result, "single_data": pipe_dict}
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
            pipe_id = data_dict["pipe_id"]
        except KeyError as e:
            context = {"code": 1, "msg": "数据管道标识不能为空"}
            return JsonResponse(context)
        try:
            pipe_name = data_dict["pipe_name"]
        except KeyError as e:
            context = {"code": 1, "msg": "数据管道名称不能为空"}
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
        try:
            tool = DataPipe.objects.get(pipe_id=pipe_id)
        except Exception as e:
            tool = False
        if tool:
            context = {"code": 1, "msg": "数据管道标识已存在，请重新输入"}
            return JsonResponse(context)
        if not re.match(r"^[a-zA-Z0-9_]{4,16}$", str(pipe_id)):
            context = {"code": 1, "msg": "数据管道标识为4－16位的字母,数字或下划线"}
            return JsonResponse(context)
        try:
            datapipe = DataPipe()
            datapipe.pipe_id = pipe_id
            datapipe.pipe_name = pipe_name
            datapipe.template = template
            datapipe.script = script
            datapipe.remark = remark
            datapipe.pipe_user = user
            datapipe.save()
        except Exception as e:
            context = {"code": 1, "msg": "添加数据管道失败"}
            return JsonResponse(context)
        context = {"code": 0, "msg": "添加数据管道成功"}
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
            pipe_id = data_dict["pipe_id"]
        except KeyError as e:
            context = {"code": 1, "msg": "数据源标识不能为空"}
            return JsonResponse(context)
        try:
            pipe_name = data_dict["pipe_name"]
        except KeyError as e:
            context = {"code": 1, "msg": "数据源名称不能为空"}
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
        if not all([id, pipe_id, pipe_name]):
            context = {"code": 1, "msg": "参数不完整"}
            return JsonResponse(context)
        if not re.match(r"^[a-zA-Z0-9_]{4,16}$", str(pipe_id)):
            context = {"code": 1, "msg": "数据管道标识为4－16位的字母,数字或下划线"}
            return JsonResponse(context)
        try:
            datapipe = DataPipe.objects.get(id=id, pipe_user=user_id)
            datapipe.pipe_id = pipe_id
            datapipe.pipe_name = pipe_name
            datapipe.template = template
            datapipe.script = script
            datapipe.remark = remark
            datapipe.is_available = is_available
            datapipe.pipe_user = user
            datapipe.save()
        except Exception as e:
            context = {"code": 1, "msg": "修改数据管道失败"}
            return JsonResponse(context)
        context = {"code": 0, "msg": "修改数据管道成功"}
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
            DataPipe.objects.filter(id=id, pipe_user=user_id).delete()
        except Exception as e:
            context = {"code": 1, "msg": "删除数据管道失败"}
            return JsonResponse(context)
        context = {"code": 0, "msg": "删除数据管道成功"}
        return JsonResponse(context)


class SourceApi(View):
    def get(self, request):
        context = LoginRequiredMixin.login_required(request)
        if context["code"] != 0:
            return JsonResponse(context)
        user_id = context["user_id"]
        data_source_list = DataSource.objects.filter(source_user=user_id).order_by("id")
        if not data_source_list:
            context = {"code": 0, "msg": "还未有数据源注册", "data": {}}
            return JsonResponse(context)
        all_data_source_list = []
        for source in data_source_list:
            data_dict = dict()
            data_dict["id"] = source.id
            data_dict["source_name"] = source.source_name
            data_dict["source_id"] = source.source_id
            all_data_source_list.append(data_dict)
        data = {"all_data": all_data_source_list}
        context = {"code": 0, "msg": "获取数据成功", "data": data}
        return JsonResponse(context)


class PipeApi(View):
    def get(self, request):
        context = LoginRequiredMixin.login_required(request)
        if context["code"] != 0:
            return JsonResponse(context)
        user_id = context["user_id"]
        data_pipe_list = DataPipe.objects.filter(pipe_user=user_id).order_by("id")
        if not data_pipe_list:
            context = {"code": 0, "msg": "还未有数据源注册", "data": {}}
            return JsonResponse(context)
        all_data_pipe_list = []
        for pipe in data_pipe_list:
            data_dict = dict()
            data_dict["id"] = pipe.id
            data_dict["pipe_name"] = pipe.pipe_name
            data_dict["pipe_id"] = pipe.pipe_id
            all_data_pipe_list.append(data_dict)
        data = {"all_data": all_data_pipe_list}
        context = {"code": 0, "msg": "获取数据成功", "data": data}
        return JsonResponse(context)
