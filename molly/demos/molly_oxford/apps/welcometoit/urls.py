from django.conf.urls.defaults import *

from .views import IndexView

urlpatterns = patterns('',
   (r'^$', IndexView, {}, 'index'),
   (r'^(?P<section>[a-z]+)/$', IndexView, {}, 'index'),
   (r'^(?P<section>[a-z]+)/(?P<subsection>[a-z_\d.]+)/$', IndexView, {}, 'index'),
)