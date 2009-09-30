from django.http import HttpResponse

class BaseView(object):
    def method_not_acceptable(self, request):
        response = HttpResponse(
            'You may not perform a %s request against this resource.' % request.method,
            status=405,
        )
        
    def bad_request(self, request):
        response = HttpResponse(
            'Your request was malformed.',
            status=400,
        )
        
    def initial_context(self, request, *args, **kwargs):
        return {}
        
    def __call__(self, request, *args, **kwargs):
        method_name = 'handle_%s' % request.method
        if hasattr(self, method_name):
            context = self.initial_context(request, *args, **kwargs)
            return getattr(self, method_name)(request, context, *args, **kwargs)
        else:
            return method_not_acceptable(request)

    @property
    def __name__(self):
        return type(self).__name__