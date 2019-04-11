from django.views.generic import View
from django.http import JsonResponse
from users.models import User
from util.commons import LoginRequiredMixin
from util.constants import APIQ_PRO_URL
from .models import AnalysisParameter, OptimizationParameter
from object.models import Object
import json
import re
import ast
import requests


class AnalysisView(View):
    def __init__(self):
        super(AnalysisView, self).__init__()
        self.template = ""
        self.remark = ""
        self.version = ""

    def get_single_data(self, id, user_id):
        analysis = AnalysisParameter.objects.filter(id=id, analysis_user=user_id).first()
        analysis_dict = dict()
        analysis_dict["id"] = analysis.id
        analysis_dict["ana_para_id"] = analysis.ana_para_id
        analysis_dict["ana_para_name"] = analysis.ana_para_name
        analysis_dict["script"] = analysis.script
        analysis_dict["template"] = analysis.template
        analysis_dict["version"] = analysis.version
        analysis_dict["remark"] = analysis.remark
        analysis_dict["reference"] = analysis.reference
        analysis_dict["object_id"] = analysis.object_id.object_id
        analysis_dict["date_created"] = str(analysis.date_created)[:19]
        analysis_dict["is_available"] = analysis.is_available
        return analysis_dict

    def get(self, request):
        context = LoginRequiredMixin.login_required(request)
        if context["code"] != 0:
            return JsonResponse(context)
        user_id = context["user_id"]
        analysis_list = AnalysisParameter.objects.filter(analysis_user=user_id).order_by("id")
        if not analysis_list:
            context = {"code": 0, "msg": "未有分析参数创建", "data": {"all_data": [], "single_data": {}}}
            return JsonResponse(context)
        id = request.GET.get("id")
        keyword = request.GET.get("keyword")
        if not keyword:
            if not id:
                id = analysis_list[0].id
                all_analysis_data_list = list()
                for analysis in analysis_list:
                    data_dict = dict()
                    data_dict["id"] = analysis.id
                    data_dict["ana_para_id"] = analysis.ana_para_id
                    data_dict["ana_para_name"] = analysis.ana_para_name
                    all_analysis_data_list.append(data_dict)
                analysis_dict = self.get_single_data(id, user_id)
                data = {"all_data": all_analysis_data_list, "single_data": analysis_dict}
                context = {"code": 0, "msg": "获取分析参数页面成功", "data": data}
                return JsonResponse(context)
            else:
                analysis_dict = self.get_single_data(id, user_id)
                data = {"single_data": analysis_dict}
                context = {"code": 0, "msg": "获取分析参数页面成功", "data": data}
                return JsonResponse(context)
        else:
            keyword = keyword.strip(" ")
            search_result = list()
            for analysis in analysis_list:
                analysis_dict = dict()
                if (keyword.upper() in analysis.ana_para_id.upper()) or (
                            keyword.upper() in analysis.ana_para_name.upper()):
                    analysis_dict["id"] = analysis.id
                    analysis_dict["ana_para_id"] = analysis.ana_para_id
                    analysis_dict["ana_para_name"] = analysis.ana_para_name
                if analysis.ana_para_name.upper() in keyword.upper():
                    analysis_dict["id"] = analysis.id
                    analysis_dict["ana_para_id"] = analysis.ana_para_id
                    analysis_dict["ana_para_name"] = analysis.ana_para_name
                if analysis_dict:
                    search_result.append(analysis_dict)
            if not search_result:
                data = {"all_data": search_result, "single_data": {}}
                context = {"code": 0, "msg": "搜索的内容不存在", "data": data}
                return JsonResponse(context)
            id = search_result[0]["id"]
            analysis_dict = self.get_single_data(id, user_id)
            data = {"all_data": search_result, "single_data": analysis_dict}
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
            ana_para_id = data_dict["ana_para_id"]
        except KeyError as e:
            context = {"code": 1, "msg": "分析参数标识不能为空"}
            return JsonResponse(context)
        try:
            ana_para_name = data_dict["ana_para_name"]
        except KeyError as e:
            context = {"code": 1, "msg": "分析参数名称不能为空"}
            return JsonResponse(context)
        try:
            script = data_dict["script"]
            if not script:
                context = {"code": 1, "msg": "脚本不能为空"}
                return JsonResponse(context)
        except KeyError as e:
            context = {"code": 1, "msg": "脚本不能为空"}
            return JsonResponse(context)
        try:
            object_id = data_dict["object_id"]
        except KeyError as e:
            context = {"code": 1, "msg": "分析对象标识不能为空"}
            return JsonResponse(context)
        try:
            template = data_dict["template"]
        except KeyError as e:
            template = self.template
        try:
            remark = data_dict["remark"]
        except KeyError as e:
            remark = self.remark
        if not all([ana_para_id, ana_para_name, script, object_id]):
            context = {"code": 1, "msg": "参数不完整"}
            return JsonResponse(context)
        try:
            tool = AnalysisParameter.objects.get(ana_para_id=ana_para_id)
        except Exception as e:
            tool = False
        if tool:
            context = {"code": 1, "msg": "分析参数标识已存在，请重新输入"}
            return JsonResponse(context)
        if not re.match(r"^[a-zA-Z0-9_]{4,16}$", str(ana_para_id)):
            context = {"code": 1, "msg": "分析参数标识为4－16位的字母,数字或下划线"}
            return JsonResponse(context)
        try:
            ana_object = Object.objects.get(object_id=object_id)
        except Exception as e:
            context = {"code": 1, "msg": "分析对象不存在"}
            return JsonResponse(context)
        try:
            ast.literal_eval(script)
        except Exception as e:
            context = {"code": 1, "msg": "分析参数脚本格式错误"}
            return JsonResponse(context)
        try:
            analysis_parameter = AnalysisParameter()
            analysis_parameter.ana_para_name = ana_para_name
            analysis_parameter.ana_para_id = ana_para_id
            analysis_parameter.script = script
            analysis_parameter.object_id = ana_object
            analysis_parameter.template = template
            analysis_parameter.remark = remark
            analysis_parameter.analysis_user = user
            analysis_parameter.save()
        except Exception as e:
            context = {"code": 1, "msg": "数据库添加分析参数信息失败"}
            return JsonResponse(context)
        context = {"code": 0, "msg": "添加分析参数成功"}
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
            ana_object_id = Object.objects.get(object_id=data_dict["object_id"])
        except Exception:
            context = {"code": 1, "msg": "分析对象ID不能为空"}
            return JsonResponse(context)
        try:
            id = data_dict["id"]
        except KeyError as e:
            context = {"code": 1, "msg": "分析参数错误，请刷新页面重试"}
            return JsonResponse(context)
        try:
            ana_para_id = data_dict["ana_para_id"]
        except KeyError as e:
            context = {"code": 1, "msg": "分析参数标识不能为空"}
            return JsonResponse(context)
        try:
            ana_para_name = data_dict["ana_para_name"]
        except KeyError as e:
            context = {"code": 1, "msg": "分析参数名不能为空"}
            return JsonResponse(context)
        try:
            script = data_dict["script"]
            if not script:
                context = {"code": 1, "msg": "脚本不能为空"}
                return JsonResponse(context)
        except KeyError as e:
            context = {"code": 1, "msg": "脚本不能为空"}
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
            remark = data_dict["remark"]
        except KeyError as e:
            remark = self.remark
        if not re.match(r"^[a-zA-Z0-9_]{4,16}$", str(ana_para_id)):
            context = {"code": 1, "msg": "分析参数标识为4－16位的字母,数字或下划线"}
            return JsonResponse(context)
        try:
            ast.literal_eval(script)
        except Exception as e:
            context = {"code": 1, "msg": "分析参数脚本格式错误"}
            return JsonResponse(context)
        try:
            analysis_parameter = AnalysisParameter.objects.get(id=id, analysis_user=user_id)
            analysis_parameter.ana_para_name = ana_para_name
            analysis_parameter.ana_para_id = ana_para_id
            analysis_parameter.script = script
            analysis_parameter.object_id = ana_object_id
            analysis_parameter.template = template
            analysis_parameter.is_available = is_available
            analysis_parameter.remark = remark
            analysis_parameter.analysis_user = user
            analysis_parameter.save()
        except Exception as e:
            print(e)
            context = {"code": 1, "msg": "修改分析参数失败"}
            return JsonResponse(context)
        context = {"code": 0, "msg": "修改分析参数成功"}
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
            AnalysisParameter.objects.filter(id=id, analysis_user=user_id).delete()
        except Exception as e:
            context = {"code": 1, "msg": "删除分析参数失败"}
            return JsonResponse(context)
        context = {"code": 0, "msg": "删除分析参数成功"}
        return JsonResponse(context)


class OptimizationView(View):
    def __init__(self):
        super(OptimizationView, self).__init__()
        self.template = ""
        self.remark = ""

    def get_single_data(self, id, user_id):
        optimization = OptimizationParameter.objects.filter(id=id, optimization_user=user_id).first()
        optimization_dict = dict()
        optimization_dict["id"] = optimization.id
        optimization_dict["opt_para_id"] = optimization.opt_para_id
        optimization_dict["opt_para_name"] = optimization.opt_para_name
        optimization_dict["script"] = optimization.script
        optimization_dict["object_id"] = optimization.object_id.object_id
        optimization_dict["template"] = optimization.template
        optimization_dict["version"] = optimization.version
        optimization_dict["remark"] = optimization.remark
        optimization_dict["reference"] = optimization.reference
        optimization_dict["date_created"] = str(optimization.date_created)[:19]
        optimization_dict["is_available"] = optimization.is_available
        return optimization_dict

    def get(self, request):
        context = LoginRequiredMixin.login_required(request)
        if context["code"] != 0:
            return JsonResponse(context)
        user_id = context["user_id"]
        optimization_list = OptimizationParameter.objects.filter(optimization_user=user_id).order_by("id")
        if not optimization_list:
            context = {"code": 0, "msg": "还未有优化参数创建", "data": {"all_data": [], "single_data": {}}}
            return JsonResponse(context)
        id = request.GET.get("id")
        keyword = request.GET.get("keyword")
        if not keyword:
            if not id:
                id = optimization_list[0].id
                all_optimization_data_list = list()
                for optimization in optimization_list:
                    data_dict = dict()
                    data_dict["id"] = optimization.id
                    data_dict["opt_para_id"] = optimization.opt_para_id
                    data_dict["opt_para_name"] = optimization.opt_para_name
                    all_optimization_data_list.append(data_dict)
                optimization_dict = self.get_single_data(id, user_id)
                data = {"all_data": all_optimization_data_list, "single_data": optimization_dict}
                context = {"code": 0, "msg": "获取优化参数页面成功", "data": data}
                return JsonResponse(context)
            else:
                try:
                    optimization_dict = self.get_single_data(id, user_id)
                except Exception as e:
                    context = {"code": 1, "msg": "获取数据失败，请确认分析对象成功填写"}
                    return JsonResponse(context)
                data = {"single_data": optimization_dict}
                context = {"code": 0, "msg": "获取优化参数页面成功", "data": data}
                return JsonResponse(context)
        else:
            keyword = keyword.strip(" ")
            search_result = list()
            for optimization in optimization_list:
                optimization_dict = dict()
                if (keyword.upper() in optimization.opt_para_id.upper()) or (
                            keyword.upper() in optimization.opt_para_name.upper()):
                    optimization_dict["id"] = optimization.id
                    optimization_dict["opt_para_id"] = optimization.opt_para_id
                    optimization_dict["opt_para_name"] = optimization.opt_para_name
                if optimization.opt_para_name.upper() in keyword.upper():
                    optimization_dict["id"] = optimization.id
                    optimization_dict["opt_para_id"] = optimization.opt_para_id
                    optimization_dict["opt_para_name"] = optimization.opt_para_name
                if optimization_dict:
                    search_result.append(optimization_dict)
            if not search_result:
                data = {"all_data": search_result, "single_data": {}}
                context = {"code": 0, "msg": "搜索的内容不存在", "data": data}
                return JsonResponse(context)
            id = search_result[0]["id"]
            try:
                optimization_dict = self.get_single_data(id, user_id)
            except Exception as e:
                context = {"code": 1, "msg": "获取数据失败，请确认分析对象成功填写"}
                return JsonResponse(context)
            data = {"all_data": search_result, "single_data": optimization_dict}
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
            opt_para_id = data_dict["opt_para_id"]
        except KeyError as e:
            context = {"code": 1, "msg": "优化参数标识不能为空"}
            return JsonResponse(context)
        try:
            opt_para_name = data_dict["opt_para_name"]
        except KeyError as e:
            context = {"code": 1, "msg": "优化参数名不能为空"}
            return JsonResponse(context)
        try:
            script = data_dict["script"]
            if not script:
                context = {"code": 1, "msg": "脚本不能为空不能为空"}
                return JsonResponse(context)
        except KeyError:
            context = {"code": 1, "msg": "脚本格式错误"}
            return JsonResponse(context)
        try:
            object_id = data_dict["object_id"]
        except KeyError as e:
            context = {"code": 1, "msg": "分析对象标识不能为空"}
            return JsonResponse(context)
        try:
            template = data_dict["template"]
        except KeyError as e:
            template = self.template
        try:
            remark = data_dict["remark"]
        except KeyError as e:
            remark = self.remark
        if not all([opt_para_id, opt_para_name, script, object_id]):
            context = {"code": 1, "msg": "参数不完整"}
            return JsonResponse(context)
        if not re.match(r"^[a-zA-Z0-9_]{4,16}$", str(opt_para_id)):
            context = {"code": 1, "msg": "优化参数标识为4－16位的字母,数字或下划线"}
            return JsonResponse(context)
        try:
            opt_object = Object.objects.get(object_id=object_id)
        except Exception:
            context = {"code": 1, "msg": "分析对象ID不存在"}
            return JsonResponse(context)
        try:
            ast.literal_eval(script)
        except Exception as e:
            context = {"code": 1, "msg": "优化参数脚本格式错误"}
            return JsonResponse(context)
        try:
            optimization_parameter = OptimizationParameter()
            optimization_parameter.opt_para_id = opt_para_id
            optimization_parameter.opt_para_name = opt_para_name
            optimization_parameter.script = script
            optimization_parameter.object_id = opt_object
            optimization_parameter.template = template
            optimization_parameter.remark = remark
            optimization_parameter.optimization_user = user
            optimization_parameter.save()
        except Exception as e:
            context = {"code": 1, "msg": "添加优化参数错误"}
            return JsonResponse(context)
        context = {"code": 0, "msg": "添加优化参数成功"}
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
            opt_para_id = data_dict["opt_para_id"]
        except KeyError as e:
            context = {"code": 1, "msg": "优化参数标识不能为空"}
            return JsonResponse(context)
        try:
            opt_para_name = data_dict["opt_para_name"]
        except KeyError as e:
            context = {"code": 1, "msg": "优化参数名不能为空"}
            return JsonResponse(context)
        try:
            script = data_dict["script"]
            if not script:
                context = {"code": 1, "msg": "script不能为空"}
                return JsonResponse(context)
        except KeyError:
            context = {"code": 1, "msg": "script不能为空"}
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
            opt_object_id = Object.objects.get(object_id=data_dict["object_id"])
        except Exception:
            context = {"code": 1, "msg": "分析对象ID不能为空"}
            return JsonResponse(context)
        try:
            remark = data_dict["remark"]
        except KeyError as e:
            remark = self.remark
        if not all([id, opt_para_id, opt_para_name, script]):
            context = {"code": 1, "msg": "参数不完整"}
            return JsonResponse(context)
        if not re.match(r"^[a-zA-Z0-9_]{4,16}$", str(opt_para_id)):
            context = {"code": 1, "msg": "优化参数标识为4－16位的字母,数字或下划线"}
            return JsonResponse(context)
        try:
            ast.literal_eval(script)
        except Exception as e:
            context = {"code": 1, "msg": "优化参数脚本格式错误"}
            return JsonResponse(context)
        try:
            optimization_parameter = OptimizationParameter.objects.get(id=id)
            optimization_parameter.opt_para_id = opt_para_id
            optimization_parameter.opt_para_name = opt_para_name
            optimization_parameter.script = script
            optimization_parameter.object_id = opt_object_id
            optimization_parameter.template = template
            optimization_parameter.is_available = is_available
            optimization_parameter.remark = remark
            optimization_parameter.optimization_user = user
            optimization_parameter.save()
        except Exception as e:
            context = {"code": 1, "msg": "修改优化参数信息失败"}
            return JsonResponse(context)
        context = {"code": 0, "msg": "修改优化参数信息成功"}
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
            OptimizationParameter.objects.filter(id=id, optimization_user=user_id).delete()
        except Exception as e:
            context = {"code": 1, "msg": "删除参数失败"}
            return JsonResponse(context)
        context = {"code": 0, "msg": "删除参数成功"}
        return JsonResponse(context)


class AnalysisApi(View):
    def get(self, request):
        context = LoginRequiredMixin.login_required(request)
        if context["code"] != 0:
            return JsonResponse(context)
        user_id = context["user_id"]
        analysis_list = AnalysisParameter.objects.filter(analysis_user=user_id).order_by("id")
        if not analysis_list:
            context = {"code": 0, "msg": "分析参数为空", "data": {}}
            return JsonResponse(context)
        all_analysis_data_list = list()
        for analysis in analysis_list:
            data_dict = dict()
            data_dict["id"] = analysis.id
            data_dict["ana_para_id"] = analysis.ana_para_id
            data_dict["ana_para_name"] = analysis.ana_para_name
            all_analysis_data_list.append(data_dict)
        data = {"all_data": all_analysis_data_list}
        context = {"code": 0, "msg": "获取数据成功", "data": data}
        return JsonResponse(context)


class OptimizationApi(View):
    def get(self, request):
        context = LoginRequiredMixin.login_required(request)
        if context["code"] != 0:
            return JsonResponse(context)
        user_id = context["user_id"]
        optimization_list = OptimizationParameter.objects.filter(optimization_user=user_id).order_by("id")
        if not optimization_list:
            context = {"code": 0, "msg": "优化参数为空", "data": {}}
            return JsonResponse(context)
        all_optimization_data_list = list()
        for optimization in optimization_list:
            data_dict = dict()
            data_dict["id"] = optimization.id
            data_dict["opt_para_name"] = optimization.opt_para_name
            data_dict["opt_para_id"] = optimization.opt_para_id
            all_optimization_data_list.append(data_dict)
        data = {"all_data": all_optimization_data_list}
        context = {"code": 0, "msg": "获取数据成功", "data": data}
        return JsonResponse(context)


class GetMappingView(View):
    def get(self, request):
        context = LoginRequiredMixin.login_required(request)
        if context["code"] != 0:
            return JsonResponse(context)
        object_id = request.GET.get("object_id")
        if not object_id:
            context = {"code": 1, "msg": "object_id不能为空"}
            return JsonResponse(context)
        data = {"equipment_id": object_id}
        try:
            response = requests.post(APIQ_PRO_URL, data=data)
            content = json.loads(response.text)
        except Exception as e:
            context = {"code": 1, "msg": "indass请求mapping数据出错"}
            return JsonResponse(context)
        if content["code"] != 200:
            context = {"code": 1, "msg": "indass请求mapping数据出错"}
            return JsonResponse(context)
        all_data = content["info"]["script"]
        data = {"all_data": all_data}
        context = {"code": 0, "msg": "获取mapping数据成功", "data": data}
        return JsonResponse(context)
