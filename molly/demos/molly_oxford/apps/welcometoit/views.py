import urllib2

from lxml import etree

from molly.utils.views import BaseView
from molly.utils.xslt import transform
from molly.utils.breadcrumbs import *

class IndexView(BaseView):
    _BASE_URL = 'http://www.oucs.ox.ac.uk/welcometoit/'
    
    @BreadcrumbFactory
    def breadcrumb(cls, request, context, section=None, subsection=None):
        if subsection:
            parent = lazy_parent(IndexView, section=section)
            reverse_args = [section, subsection]
        elif section:        
            parent = lazy_parent(IndexView)
            reverse_args = [section]
        else:
            parent = None
            reverse_args = []

        if not section:
            title = 'Welcome to IT'
        elif context['subsection'] != subsection:
            title = {
                'unwelcome': 'Online Security',
                'bringing': 'Bringing Your Own Computer?',
                'using': 'Using Any Computer',
                'about': 'About Oxford University',
            }.get(section, 'Up')
        else:
            title = context['title']
        
        return Breadcrumb(
            cls.conf.local_name, 
            parent,
            title, 
            lazy_reverse('welcometoit:index', args=reverse_args),
        )
    
    def initial_context(cls, request, section=None, subsection=None):
        xml = etree.parse(
            urllib2.urlopen(
                cls.get_url(section, subsection)),
            parser=etree.HTMLParser())
            
        xml = transform(xml, 'welcometoit/index.xslt')
        title = xml.find('.//h2')
        return {
            'section': section,
            'subsection': subsection,
            'title': title.text or 'Up&hellip;',
            'page': etree.tostring(xml, method='html')
        }
    
    def handle_GET(cls, request, context, section=None, subsection=None):
        return cls.render(request, context, 'welcometoit/index')

    def get_url(cls, section=None, subsection=None):
        url = cls._BASE_URL
        if section:
            url += section + '.xml'
        if subsection:
            url += '.ID=' + subsection
        return url