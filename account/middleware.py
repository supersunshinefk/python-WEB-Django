from django.http import QueryDict

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object


class HttpMethodMiddleware(MiddlewareMixin):
    def process_request(self, request):
        try:
            http_method = request.META['REQUEST_METHOD']
            if http_method.upper() not in ('GET', 'POST'):
                setattr(request, http_method.upper(), QueryDict(request.body))
        except Exception:
            pass
        finally:
            return None
