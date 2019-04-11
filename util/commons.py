from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings
from util import constants
from django.core.cache import cache
import re
import redis
from indass_boss import settings

class LoginRequiredMixin(object):
    @classmethod
    def login_required(cls, request):
        try:
            token = request.META["HTTP_AUTHORIZATION"]
        except Exception as e:
            context = {"code": 3, "msg": "用户未登录"}
            return context
        s = Serializer(settings.SECRET_KEY, constants.USER_TOKEN_EXPIRES)
        try:
            user_data = s.loads(token)
        except Exception as e:
            context = {"code": 3, "msg": "用户未登录"}
            return context
        try:
            user_id = int(user_data.get("user_id"))
        except Exception as e:
            context = {"code": 3, "msg": "token错误"}
            return context
        token_name = "token_%d" % user_id
        cache_token = cache.get(token_name)
        if not cache_token:
            context = {"code": 3, "msg": "由于您太久未操作，请重新登录"}
            return context
        if token != cache_token:
            context = {"code": 3, "msg": "用户未登录"}
            return context
        cache.set(token_name, token, timeout=constants.USER_CACHE_TOKEN_EXPIRES)
        context = {"code": 0, "msg": "用户已登录", "user_id": user_id}
        return context


class FilterScriptVerify(object):
    @classmethod
    def script_verify(cls, new_script):
        try:
            if not new_script and not new_script[0]:
                msg = "请输入正确的过滤器脚本数据"
                context = {"code": 1, "msg": msg}
                return context
            if (type(new_script) and type(new_script[0])) is list :
                for len_ in range(len(new_script)):
                    if not new_script[len_][1].startswith("@"):
                        msg = u'第 %d 个参数的 %s 程序不是以 @ 开头' % (len_ + 1, new_script[len_][1])
                        context = {"code": 1, "msg": msg}
                        return context
                    if len(new_script[len_]) != 3:
                        msg = "脚本中第%d行列表长度不等于3！" % (len_ + 1)
                        context = {"code": 1, "msg": msg}
                        return context
                    if re.findall(r"(\s+)", new_script[len_][0]):
                        msg = "脚本的第%d行的参数名处存在空格！" % (len_ + 1)
                        context = {"code": 1, "msg": msg}
                        return context
                    if re.findall(r"(\s+)", new_script[len_][1]):
                        msg = "脚本的第%d行的运算符处存在空格！" % (len_ + 1)
                        context = {"code": 1, "msg": msg}
                        return context
            
        except Exception as e:
            context = {"code": 1, "msg": "请按照规范输入脚本!"}
            return context
        context = {"code": 0, "msg": "脚本验证成功"}
        return context


class OrganizerScriptVerify(object):
    @classmethod
    def script_verify(cls, new_script):
        try:
            if not new_script:
                msg = "请输入正确的组织器脚本数据"
                context = {"code": 1, "msg": msg}
                return context
            if type(new_script) is dict:
                if 'all_parameter' in new_script.keys():
                    all_parameter = new_script['all_parameter']
                    for all_param in all_parameter:
                        if type(all_param) is not str:
                            msg = "脚本all_parameter中的每个元素应为字符类型"
                            context = {"code": 1, "msg": msg}
                            return context
                        if all_param.isspace() is True:
                            context = {"code": 1, "msg": "The Script of 'all_parameter' have empty string!"}
                            return context
                        if re.findall(r"(\s+)", all_param):
                            msg = "脚本中all_parameter的%s处存在空格！" % all_param
                            context = {"code": 1, "msg": msg}
                            return context
                if 'analysis_parameter' in new_script.keys():
                    analysis_parameter = new_script['analysis_parameter']
                    for len_ in range(len(analysis_parameter)):
                        if analysis_parameter[len_][0].isspace() and analysis_parameter[len_][1].isspace() is True:
                            context = {"code": 1, "msg": "The Script of 'analysis_parameter' have empty string!"}
                            return context
                        if len(analysis_parameter[len_]) != 2:
                            msg = "脚本中optimization_parameter第%d行列表长度不等于2！" % (len_ + 1)
                            context = {"code": 1, "msg": msg}
                            return context
                        if re.findall(r"(\s+)", analysis_parameter[len_][0]):
                            msg = "脚本中analysis_parameter第%d行变量名存在空格！" % (len_ + 1)
                            context = {"code": 1, "msg": msg}
                            return context
                        if re.findall(r"(\s+)", analysis_parameter[len_][1]):
                            msg = "脚本中analysis_parameter第%d行参数名存在空格！" % (len_ + 1)
                            context = {"code": 1, "msg": msg}
                            return context
                if 'optimization_parameter' in new_script.keys():
                    optimization_parameter = new_script['optimization_parameter']
                    for len_ in range(len(optimization_parameter)):
                        if optimization_parameter[len_][0].isspace() and optimization_parameter[len_][1].isspace():
                            context = {"code": 1,
                                       "msg": "The Script of 'optimization_parameter' have empty string!"}
                            return context
                        if len(optimization_parameter[len_]) != 2:
                            msg = "脚本中optimization_parameter第%d行列表长度不等于2！!" % (len_ + 1)
                            context = {"code": 1, "msg": msg}
                            return context
                        if re.findall(r"(\s+)", optimization_parameter[len_][0]):
                            msg = "脚本中analysis_parameter第%d行变量名存在空格！" % (len_ + 1)
                            context = {"code": 1, "msg": msg}
                            return context
                        if re.findall(r"(\s+)", optimization_parameter[len_][1]):
                            msg = "脚本中analysis_parameter第%d行参数名存在空格！" % (len_ + 1)
                            context = {"code": 1, "msg": msg}
                            return context

        except Exception as e:
            context = {"code": 1, "msg": "请按照规范输入脚本!"}
            return context
        context = {"code": 0, "msg": "脚本验证成功"}
        return context
        

class MixRedis:
    def __init__(self):
        self.conn = None
        self.config = settings.REDIS_CONFIG

    def connect(self):
        """
        redis连接
        :return
        """
        self.conn = redis.Redis(**self.config)
