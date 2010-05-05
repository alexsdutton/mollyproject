from xml.sax.saxutils import escape
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404

from mobile_portal.core.ldap_queries import get_person_units
from mobile_portal.core.renderers import mobile_render
from mobile_portal.core.handlers import BaseView

from models import RSSFeed, RSSItem

class IndexView(BaseView):
    def get_metadata(self, request):
        return {
            'title': 'News',
            'additional': 'View news feeds and events from across the University.',
        }
        
    def handle_GET(self, request, context):
        feeds = RSSFeed.objects.all()
        context = {
            'feeds': feeds,
        }
        return mobile_render(request, context, 'rss/index')

class ItemListView(BaseView):
    def get_metadata(self, request, slug):
        feed = get_object_or_404(RSSFeed, slug=slug)
        
        return {
            'last_modified': feed.last_modified,
            'title': feed.title,
            'additional': '<strong>News feed</strong>, last updated: %s' % feed.last_modified.strftime('%a, %d %b %Y'),
        }
        
    def handle_GET(self, request, context, slug):
        feed = get_object_or_404(RSSFeed, slug=slug)
        context['feed'] = feed
        return mobile_render(request, context, 'rss/item_list')

class ItemDetailView(BaseView):
    def get_metadata(self, request, slug, id):
        item = get_object_or_404(RSSItem, feed__slug=slug, id=id)
        
        return {
            'last_modified': item.last_modified,
            'title': item.title,
            'additional': '<strong>News item</strong>, %s, %s' % (escape(item.feed.title), item.last_modified.strftime('%a, %d %b %Y')),
        }
        
    def handle_GET(self, request, context, slug, id):
        item = get_object_or_404(RSSItem, feed__slug=slug, id=id)
        context.update({
            'item': item,
            'description': item.get_description_display(request.device)
        })
        return mobile_render(request, context, 'rss/item_detail')
