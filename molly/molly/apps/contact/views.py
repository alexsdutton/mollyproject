import simplejson, hashlib, urllib

# parse_qsl was moved from cgi to urlparse in Py2.6.
try:
    from urlparse import parse_qsl
except ImportError, e:
    from cgi import parse_qsl

from django.http import HttpResponse
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.template import RequestContext

from molly.utils.views import BaseView, renderer
from molly.utils.breadcrumbs import *

from .forms import GenericContactForm

class IndexView(BaseView):
    @BreadcrumbFactory
    def breadcrumb(self, request, context):
        return Breadcrumb(
            self.conf.local_name,
            None,
            'Contact search',
            lazy_reverse('index'),
        )

    def initial_context(self, request):
        return {
            'form': self.conf.provider.form(request.GET or None),
            'medium_choices': self.conf.provider.medium_choices,
        }

    def handle_GET(self, request, context):
        return self.render(request, context, 'contact/index')

class ResultListView(IndexView):

    @BreadcrumbFactory
    def breadcrumb(self, request, context):
        return Breadcrumb(
            self.conf.local_name,
            None,
            'Contact search',
            lazy_reverse('result_list'),
        )

    def handle_GET(self, request, context):
        provider = self.conf.provider

        form = provider.form(request.GET or None)
        medium = request.GET.get('medium')
        if not medium in [m[0] for m in provider.medium_choices]:
            medium = provider.medium_choices[0][0]

        if form.is_valid():

            try:
                page = int(request.GET.get('page', '1'))
            except ValueError:
                page = 1

            query = provider.normalize_query(form.cleaned_data, medium)

            if provider.handles_pagination:
                paginator = provider.perform_query(page=page, **query)
            else:
                people = provider.perform_query(**query)
                paginator = Paginator(people, 10)

            if not (1 <= page <= paginator.num_pages):
                return self.handle_error(
                    request, context,
                    'There are no results for this page.',
                )
            page = paginator.page(page)

            query_string = dict(parse_qsl(request.META.get('QUERY_STRING', '')))
            query_string.pop('page', None)
            query_string.pop('format', None)

            context.update({
                'page': page,
                'results': paginator,
                'medium': medium,
                'query_string': urllib.urlencode(query_string),
            })

        context['form'] = form
        return self.render(request, context, 'contact/result_list')

    def handle_error(self, request, context, message):
        context.update({
            'message': message,
        })

        return self.render(request, context, 'contact/result_list')

    @renderer(format='update')
    def render_update(self, request, context, template_name):
        new_context = {
            'page_number': context['page'].number,
            'page_count': context['results'].num_pages,
            'people': [],
        }
        for result in context['page'].object_list:
            context['person'] = result
            new_context['people'].append(render_to_string(
                'contact/result.html', context,
                context_instance=RequestContext(request)))

        return self.render_json(request, new_context, template_name)

class ResultDetailView(BaseView):
    @BreadcrumbFactory
    def breadcrumb(self, request, context):
        return Breadcrumb(
            self.conf.local_name,
            None,
            'Contact search',
            lazy_reverse('result_detail'),
        )

    def handle_GET(self, request, context, id):
        try:
            context['result'] = self.conf.provider.fetch_result(id)
        except BaseContactProvider.NoSuchResult:
            raise Http404

        return self.render(request, context, 'context/result_detail')
