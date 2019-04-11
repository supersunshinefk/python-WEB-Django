from django.views.generic import View
from django.http import JsonResponse
from .models import AnalyticProject
from util.commons import LoginRequiredMixin
from account.models import Account
from source.models import DataPipe, DataSource
from preprocess.models import DataFilter, DataOrganizer
from parameter.models import AnalysisParameter, OptimizationParameter
from message.models import MessageOut
from object.models import ObjectGroup, Object
from users.models import User
from indass_boss.settings import REDIS_QUEUE
from util.commons import MixRedis
import json
import re


class ProjectView(View):
    def __init__(self):
        super(ProjectView, self).__init__()
        self.template = ""
        self.script = ""
        self.remark = ""

    def get_project_single(self, id, user_id):
        analysis = AnalyticProject.objects.filter(id=id, project_user=user_id).first()
        object_auto_id = analysis.object_id
        obj = Object.objects.get(id=object_auto_id, object_user=user_id)
        object_id = obj.object_id
        analysis_dict = dict()
        analysis_dict["id"] = analysis.id
        analysis_dict["project_id"] = analysis.project_id
        analysis_dict["project_name"] = analysis.project_name
        analysis_dict["project_start_from"] = analysis.project_start_from
        analysis_dict["project_end_by"] = analysis.project_end_by
        analysis_dict["object_id"] = object_id
        analysis_dict["project_account_id"] = analysis.project_account.account_id
        analysis_dict["project_source_id"] = analysis.project_source.source_id
        analysis_dict["project_pipe_id"] = analysis.project_pipe.pipe_id
        analysis_dict["project_filter_id"] = analysis.project_filter.filter_id
        analysis_dict["project_organizer_id"] = analysis.project_organizer.organizer_id
        analysis_dict["project_obj_group_id"] = analysis.project_obj_group.obj_group_id
        analysis_dict["project_ana_para_id"] = analysis.project_ana_para.ana_para_id
        analysis_dict["project_opt_para_id"] = analysis.project_opt_para.opt_para_id
        analysis_dict["project_msg_out_id"] = analysis.project_msg_out.msg_out_id
        analysis_dict["is_available"] = analysis.is_available
        analysis_dict["remark"] = analysis.remark
        analysis_dict["template"] = analysis.template
        analysis_dict["script"] = analysis.script
        analysis_dict["version"] = analysis.version
        analysis_dict["reference"] = analysis.reference
        return analysis_dict

    def get(self, request):
        context = LoginRequiredMixin.login_required(request)
        if context["code"] != 0:
            return JsonResponse(context)
        user_id = context["user_id"]
        analysis_list = AnalyticProject.objects.filter(project_user=user_id).order_by("id")
        if not analysis_list:
            context = {"code": 0, "msg": "还未有项目注册", "data": {"all_data": [], "single_data": {}}}
            return JsonResponse(context)
        id = request.GET.get("id")
        keyword = request.GET.get("keyword")
        if not keyword:
            if not id:
                id = analysis_list[0].id
                all_analysis_data_list = list()
                for analysis in analysis_list:
                    data_dict = dict()
                    data_dict["project_id"] = analysis.project_id
                    data_dict["id"] = analysis.id
                    data_dict["project_name"] = analysis.project_name
                    data_dict["is_available"] = analysis.is_available
                    all_analysis_data_list.append(data_dict)
                single_data = self.get_project_single(id, user_id)
                data = {"all_data": all_analysis_data_list, "single_data": single_data}
                context = {"code": 0, "msg": "获取数据成功", "data": data}
                return JsonResponse(context)
            else:
                analysis_dict = self.get_project_single(id, user_id)
                data = {"single_data": analysis_dict}
                context = {"code": 0, "msg": "获取数据成功", "data": data}
                return JsonResponse(context)
        else:
            keyword = keyword.strip(" ")
            search_result = list()
            for project in analysis_list:
                project_dict = dict()
                if (keyword.upper() in project.project_id.upper()) or (keyword.upper() in project.project_name.upper()):
                    project_dict["id"] = project.id
                    project_dict["project_id"] = project.project_id
                    project_dict["project_name"] = project.project_name
                if project.project_name.upper() in keyword.upper():
                    project_dict["project_id"] = project.project_id
                    project_dict["id"] = project.id
                    project_dict["project_name"] = project.project_name
                if project_dict:
                    search_result.append(project_dict)
            if not search_result:
                data = {"all_data": search_result, "single_data": {}}
                context = {"code": 1, "msg": "搜索的内容不存在", "data": data}
                return JsonResponse(context)
            id = search_result[0]["id"]
            client_data = self.get_project_single(id, user_id)
            data = {"single_data": client_data, "all_data": search_result}
            context = {"code": 0, "msg": "获取数据成功", "data": data}
            return JsonResponse(context)

    def post(self, request):
        context = LoginRequiredMixin.login_required(request)
        if context["code"] != 0:
            return JsonResponse(context)
        user_id = context["user_id"]
        user = User.objects.get(id=user_id)
        try:
            data_dict = json.loads(request.body.decode('utf-8'))
        except Exception:
            context = {"code": 1, "msg": "获取json数据失败"}
            return JsonResponse(context)
        try:
            project_id = data_dict["project_id"]
            if not re.match(r"^[a-zA-Z0-9_]{4,16}$", str(project_id)):
                context = {"code": 1, "msg": "项目标识必须为4－16位的字母,数字或下划线"}
                return JsonResponse(context)
        except Exception as e:
            context = {"code": 1, "msg": "分析项目标识不能为空"}
            return JsonResponse(context)
        try:
            project_name = data_dict["project_name"]
        except Exception as e:
            context = {"code": 1, "msg": "分析项目名称不能为空"}
            return JsonResponse(context)
        try:
            project_msg_out_id = data_dict["project_msg_out_id"]
        except Exception as e:
            context = {"code": 1, "msg": "消息提示不能为空"}
            return JsonResponse(context)
        try:
            project_opt_para_id = data_dict["project_opt_para_id"]
        except Exception as e:
            context = {"code": 1, "msg": "优化参数不能为空"}
            return JsonResponse(context)
        try:
            project_ana_para_id = data_dict["project_ana_para_id"]
        except Exception as e:
            context = {"code": 1, "msg": "分析参数不能为空"}
            return JsonResponse(context)
        try:
            object_id = data_dict["object_id"]
        except Exception as e:
            context = {"code": 1, "msg": "分析对象不能为空"}
            return JsonResponse(context)
        try:
            project_account_id = data_dict["project_account_id"]
        except Exception as e:
            context = {"code": 1, "msg": "账户不能为空"}
            return JsonResponse(context)
        try:
            project_source_id = data_dict["project_source_id"]
        except Exception as e:
            context = {"code": 1, "msg": "数据源不能为空"}
            return JsonResponse(context)
        try:
            project_pipe_id = data_dict["project_pipe_id"]
        except Exception as e:
            context = {"code": 1, "msg": "数据管道不能为空"}
            return JsonResponse(context)
        try:
            project_filter_id = data_dict["project_filter_id"]
        except Exception as e:
            context = {"code": 1, "msg": "数据过滤器不能为空"}
            return JsonResponse(context)
        try:
            project_obj_group_id = data_dict["project_obj_group_id"]
        except Exception as e:
            context = {"code": 1, "msg": "分析对象组不能为空"}
            return JsonResponse(context)
        try:
            project_organizer_id = data_dict["project_organizer_id"]
        except Exception as e:
            context = {"code": 1, "msg": "组织器不能为空"}
            return JsonResponse(context)
        try:
            project_start_from = data_dict["project_start_from"]
            project_end_by = data_dict["project_end_by"]
            if project_start_from > project_end_by:
                context = {"code": 1, "msg": "开始时间不能大于结束时间"}
                return JsonResponse(context)
        except Exception as e:
            context = {"code": 1, "msg": "开始时间或结束时间不能为空"}
            return JsonResponse(context)
        try:
            is_available = data_dict["is_available"]
        except Exception as e:
            context = {"code": 1, "msg": "是否开启不能为空"}
            return JsonResponse(context)
        try:
            remark = data_dict["remark"]
        except Exception as e:
            remark = self.remark
        try:
            template = data_dict["template"]
        except Exception as e:
            template = self.template
        try:
            script = data_dict["script"]
        except Exception as e:
            script = self.script
        try:
            project_account = Account.objects.get(account_id=project_account_id, account_user=user_id)
            project_source = DataSource.objects.get(source_id=project_source_id, source_user=user_id)
            project_pipe = DataPipe.objects.get(pipe_id=project_pipe_id, pipe_user=user_id)
            project_filter = DataFilter.objects.get(filter_id=project_filter_id, filter_user=user_id)
            project_organizer = DataOrganizer.objects.get(organizer_id=project_organizer_id, organizer_user=user_id)
            project_ana_para = AnalysisParameter.objects.get(ana_para_id=project_ana_para_id, analysis_user=user_id)
            project_opt_para = OptimizationParameter.objects.get(opt_para_id=project_opt_para_id, optimization_user=user_id)
            project_obj_group = ObjectGroup.objects.get(obj_group_id=project_obj_group_id, obj_group_user=user_id)
            project_msg_out = MessageOut.objects.get(msg_out_id=project_msg_out_id, msg_out_user=user_id)
        except Exception as e:
            context = {"code": 1, "msg": "获取项目关联信息错误"}
            return JsonResponse(context)
        try:
            obj = Object.objects.get(object_id=object_id, object_user=user_id)
            object_auto_id = obj.id
        except Exception as e:
            context = {"code": 1, "msg": "分析对象不存在"}
            return JsonResponse(context)
        try:
            analytic_project = AnalyticProject()
            analytic_project.project_id = project_id
            analytic_project.project_name = project_name
            analytic_project.project_start_from = project_start_from
            analytic_project.project_end_by = project_end_by
            analytic_project.project_account = project_account
            analytic_project.project_source = project_source
            analytic_project.project_filter = project_filter
            analytic_project.project_pipe = project_pipe
            analytic_project.project_organizer = project_organizer
            analytic_project.project_ana_para = project_ana_para
            analytic_project.project_obj_group = project_obj_group
            analytic_project.project_opt_para = project_opt_para
            analytic_project.project_msg_out = project_msg_out
            analytic_project.object_id = object_auto_id
            analytic_project.is_available = is_available
            analytic_project.remark = remark
            analytic_project.template = template
            analytic_project.script = script
            analytic_project.project_user = user
            analytic_project.save()
        except Exception as e:
            context = {"code": 1, "msg": "增加项目失败"}
            return JsonResponse(context)
        context = {"code": 0, "msg": "添加分析项目成功"}
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
            AnalyticProject.objects.filter(id=id, project_user=user).delete()
        except Exception as e:
            context = {"code": 1, "msg": "删除失败"}
            return JsonResponse(context)
        context = {"code": 0, "msg": "删除分析项目成功"}
        return JsonResponse(context)

    def put(self, request):
        context = LoginRequiredMixin.login_required(request)
        if context["code"] != 0:
            return JsonResponse(context)
        user_id = context["user_id"]
        user = User.objects.get(id=user_id)
        try:
            data_dict = json.loads(request.body.decode('utf-8'))
        except Exception as e:
            context = {"code": 1, "msg": "获取json数据出错"}
            return JsonResponse(context)
        try:
            project_msg_out_id = data_dict["project_msg_out_id"]
        except Exception as e:
            context = {"code": 1, "msg": "消息提示不能为空"}
            return JsonResponse(context)
        try:
            is_available = data_dict["is_available"]
        except Exception as e:
            context = {"code": 1, "msg": "是否启用不能为空"}
            return JsonResponse(context)
        try:
            project_opt_para_id = data_dict["project_opt_para_id"]
        except Exception as e:
            context = {"code": 1, "msg": "优化参数不能为空"}
            return JsonResponse(context)
        try:
            object_id = data_dict["object_id"]
        except Exception as e:
            context = {"code": 1, "msg": "分析对象不能为空"}
            return JsonResponse(context)
        try:
            project_ana_para_id = data_dict["project_ana_para_id"]
        except Exception as e:
            context = {"code": 1, "msg": "分析参数不能为空"}
            return JsonResponse(context)
        try:
            id = data_dict["id"]
        except Exception as e:
            context = {"code": 1, "msg": "项目id不能为空"}
            return JsonResponse(context)
        try:
            project_id = data_dict["project_id"]
            if not re.match(r"^[a-zA-Z0-9_]{4,16}$", str(project_id)):
                context = {"code": 1, "msg": "分析项目标识必须为4－16位的字母,数字或下划线"}
                return JsonResponse(context)
        except Exception as e:
            context = {"code": 1, "msg": "分析项目标识不能为空"}
            return JsonResponse(context)
        try:
            project_name = data_dict["project_name"]
        except Exception as e:
            context = {"code": 1, "msg": "分析项目名称不能为空"}
            return JsonResponse(context)
        try:
            project_obj_group_id = data_dict["project_obj_group_id"]
        except Exception as e:
            context = {"code": 1, "msg": "分析对象组不能为空"}
            return JsonResponse(context)
        try:
            project_start_from = data_dict["project_start_from"]
            project_end_by = data_dict["project_end_by"]
            if project_start_from > project_end_by :
                context = {"code": 1, "msg": "开始时间不能大于结束时间"}
                return JsonResponse(context)
        except Exception as e:
            context = {"code": 1, "msg": "开始时间或结束时间不能为空"}
            return JsonResponse(context)
        try:
            project_account_id = data_dict["project_account_id"]
        except Exception as e:
            context = {"code": 1, "msg": "账户不能为空"}
            return JsonResponse(context)
        try:
            project_source_id = data_dict["project_source_id"]
        except Exception as e:
            context = {"code": 1, "msg": "数据源不能为空"}
            return JsonResponse(context)
        try:
            project_pipe_id = data_dict["project_pipe_id"]
        except Exception as e:
            context = {"code": 1, "msg": "数据管道不能为空"}
            return JsonResponse(context)
        try:
            project_filter_id = data_dict["project_filter_id"]
        except Exception as e:
            context = {"code": 1, "msg": "数据过滤器不能为空"}
            return JsonResponse(context)
        try:
            project_organizer_id = data_dict["project_organizer_id"]
        except Exception as e:
            context = {"code": 1, "msg": "组织器不能为空"}
            return JsonResponse(context)
        try:
            remark = data_dict["remark"]
        except Exception as e:
            remark = self.remark
        try:
            template = data_dict["template"]
        except Exception as e:
            template = self.template
        try:
            script = data_dict["script"]
        except Exception as e:
            script = self.script
        try:
            project_account = Account.objects.get(account_id=project_account_id, account_user=user_id)
            project_source = DataSource.objects.get(source_id=project_source_id, source_user=user_id)
            project_pipe = DataPipe.objects.get(pipe_id=project_pipe_id, pipe_user=user_id)
            project_filter = DataFilter.objects.get(filter_id=project_filter_id, filter_user=user_id)
            project_organizer = DataOrganizer.objects.get(organizer_id=project_organizer_id, organizer_user=user_id)
            project_ana_para = AnalysisParameter.objects.get(ana_para_id=project_ana_para_id, analysis_user=user_id)
            project_opt_para = OptimizationParameter.objects.get(opt_para_id=project_opt_para_id, optimization_user=user_id)
            project_obj_group = ObjectGroup.objects.get(obj_group_id=project_obj_group_id, obj_group_user=user_id)
            project_msg_out = MessageOut.objects.get(msg_out_id=project_msg_out_id, msg_out_user=user_id)
        except Exception as e:
            context = {"code": 1, "msg": "获取项目关联信息错误"}
            return JsonResponse(context)
        try:
            obj = Object.objects.get(object_id=object_id, object_user=user_id)
            object_auto_id = obj.id
        except Exception as e:
            context = {"code": 1, "msg": "分析对象不存在"}
            return JsonResponse(context)
        try:
            analytic_project = AnalyticProject.objects.get(id=id, project_user=user_id)
            analytic_project.project_id = project_id
            analytic_project.project_name = project_name
            analytic_project.project_start_from = project_start_from
            analytic_project.project_end_by = project_end_by
            analytic_project.project_account = project_account
            analytic_project.project_source = project_source
            analytic_project.project_filter = project_filter
            analytic_project.project_pipe = project_pipe
            analytic_project.project_organizer = project_organizer
            analytic_project.project_ana_para = project_ana_para
            analytic_project.project_obj_group = project_obj_group
            analytic_project.project_opt_para = project_opt_para
            analytic_project.project_msg_out = project_msg_out
            analytic_project.object_id = object_auto_id
            analytic_project.remark = remark
            analytic_project.template = template
            analytic_project.script = script
            analytic_project.is_available = is_available
            analytic_project.project_user = user
            analytic_project.save()
        except Exception as e:
            context = {"code": 1, "msg": "增加项目失败"}
            return JsonResponse(context)
        context = {"code": 0, "msg": "添加项目成功"}
        return JsonResponse(context)
        

class ProjectStartApiView(View):
    def __init__(self):
        super(ProjectStartApiView, self).__init__()
        self.redis = MixRedis()
        self.redis.connect()

    def post(self, request):
        context = LoginRequiredMixin.login_required(request)
        if context["code"] != 0:
            return JsonResponse(context)
        user_id = context["user_id"]
        try:
            post_data = json.loads(request.body.decode("utf-8"))
        except Exception as e:
            context = {"code": 1, "msg": "获取json数据失败"}
            return JsonResponse(context)
        try:
            id = post_data["id"]
            is_available = post_data["is_available"]
            analysis_project = AnalyticProject.objects.get(id=id, project_user=user_id)
        except KeyError as e:
            context = {"code": 1, "msg": "参数不完整"}
            return JsonResponse(context)
        if (id is None) or (id is ""):
            context = {"code": 1, "msg": "未选择分析项目"}
            return JsonResponse(context)
        if (is_available == "true") or (is_available is True):
            organizer = DataOrganizer.objects.get(organizer_id=analysis_project.project_organizer.organizer_id)
            filter = DataFilter.objects.get(filter_id=analysis_project.project_filter.filter_id)
            source = DataSource.objects.get(source_id=analysis_project.project_source.source_id)
            account = Account.objects.get(account_id=analysis_project.project_account.account_id)
            analysis = AnalysisParameter.objects.get(ana_para_id=analysis_project.project_ana_para.ana_para_id)
            message = MessageOut.objects.get(msg_out_id=analysis_project.project_msg_out.msg_out_id)
            optimization = OptimizationParameter.objects.get(opt_para_id=analysis_project.project_opt_para.opt_para_id)
            object_id = analysis_project.object_id
            analysis_object = Object.objects.get(id=object_id)
            all_object_data_list = list()
            object_dict = dict()
            object_dict["object_name"] = analysis_object.object_name
            object_dict["object_id"] = analysis_object.object_id
            object_dict["object_reference_id"] = analysis_object.object_reference_id
            object_dict["object_model"] = analysis_object.object_model
            all_object_data_list.append(object_dict)
            optimization_dict = dict()
            optimization_dict["opt_para_id"] = optimization.opt_para_id
            try:
                optimization_dict["script"] = json.loads(optimization.script)
            except Exception as e:
                optimization_dict["script"] = []
            message_dict = dict()
            message_dict["msg_out_id"] = message.msg_out_id
            try:
                message_dict["script"] = json.loads(message.script)
            except Exception as e:
                message_dict["script"] = []
            analysis_dict = dict()
            analysis_dict["ana_para_id"] = analysis.ana_para_id
            try:
                analysis_dict["script"] = json.loads(analysis.script)
            except Exception as e:
                analysis_dict["script"] = []
            client_data = dict()
            client_data["account_id"] = account.account_id
            client_data["account_name"] = account.account_name
            client_data["account_login"] = account.account_login
            client_data["account_pin"] = account.account_pin
            source_dict = dict()
            source_dict["source_id"] = source.source_id
            source_dict["source_mode"] = source.source_mode
            filter_dict = dict()
            filter_dict["filter_id"] = filter.filter_id
            try:
                filter_dict["script"] = json.loads(filter.script)
            except Exception as e:
                filter_dict["script"] = []
            organizer_dict = dict()
            organizer_dict["organizer_id"] = organizer.organizer_id
            try:
                organizer_dict["script"] = json.loads(organizer.script)
            except Exception as e:
                organizer_dict["script"] = []
            result = dict()
            result["account"] = client_data
            result["data_source"] = source_dict
            result["object"] = all_object_data_list
            result["data_filter"] = filter_dict
            result["data_organizer"] = organizer_dict
            result["analysis_parameter"] = analysis_dict
            result["optimization_parameter"] = optimization_dict
            result["message_out"] = message_dict
            result["id"] = analysis_project.id
            result["server"] = "on"
            result["project_id"] = analysis_project.project_id
            result["project_name"] = analysis_project.project_name
            json_data = json.dumps(result)
            analysis_project.is_available = is_available
            analysis_project.save()
            single_data = dict()
            single_data["id"] = analysis_project.id
            single_data["project_id"] = analysis_project.project_id
            single_data["is_available"] = analysis_project.is_available
            data = {"single_data": single_data}
            try:
                self.data_save(json_data)
                return_data = {"code": 0, "msg": "启动项目成功！", "data":data}
                return JsonResponse(return_data)
            except Exception as e:
                return_data = {"code": 1, "msg": "启动项目失败！", "data":data}
                return JsonResponse(return_data)
        elif (is_available == "false") or (is_available is False):
            result = dict()
            result["id"] = id
            result["project_id"] = analysis_project.project_id
            result["server"] = "off"
            json_data = json.dumps(result)
            analysis_project.is_available = is_available
            analysis_project.save()
            single_data = dict()
            single_data["id"] = analysis_project.id
            single_data["project_id"] = analysis_project.project_id
            single_data["is_available"] = analysis_project.is_available
            data = {"single_data": single_data}
            try:
                self.data_save(json_data)
                return_data = {"code": 0, "msg": "禁用项目成功！", "data":data}
                return JsonResponse(return_data)
            except Exception as e:
                return_data = {"code": 1, "msg": "禁用项目失败！", "data":data}
                return JsonResponse(return_data)

    def data_save(self, data):
        __LUA_SCRIPT_HGET = '''
        local auto_id = redis.call('incr',KEYS[1])
        redis.call('HSET', KEYS[2], auto_id,  KEYS[4])
        redis.call('LPUSH', KEYS[3], auto_id)
        return auto_id
        '''
        lua_script_func = self.redis.conn.register_script(__LUA_SCRIPT_HGET)
        lua_script_func(keys=[REDIS_QUEUE['auto_id'], REDIS_QUEUE['hset'], REDIS_QUEUE['list'], data], args=[])
