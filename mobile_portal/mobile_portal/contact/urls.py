from django.conf.urls.defaults import *

urlpatterns = patterns('mobile_portal.contact.views',
    (r'^$', 'index', {}, 'contact_index'),
    (r'^quick/$', 'quick_contacts', {}, 'contact_quick'),
)
