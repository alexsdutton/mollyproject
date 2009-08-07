import simplejson, urllib, urllib2
from django import template

from mobile_portal.core.utils import AnyMethodRequest
from mobile_portal.core.models import ExternalImage, ExternalImageSized
from mobile_portal.oxpoints.models import Entity

register = template.Library()

@register.filter(name="gte")
def gte(value, arg):
    return value >= float(arg)
    
@register.filter(name="oxp_id")
def oxp_id(value):
    prefix = 'http://m.ox.ac.uk/oxpoints/id/'
    try:
        if value['uri'].startswith(prefix):
            return value['uri'][len(prefix):]
        else:
            return ""
    except:
        return ""

@register.filter(name="load_oxp_json")
def load_oxp_json(value):
    return simplejson.load(urllib.urlopen(value['uri']+'.json'))[0]
    
@register.filter(name="oxp_portal_url")
def oxp_portal_url(value):
    try:
        return Entity.objects.get(oxpoints_id=int(oxp_id(value))).get_absolute_url()
    except Entity.DoesNotExist:
        return ""
    
@register.tag(name='external_image')
def external_image(parser, token):
    args = token.split_contents()
    if len(args) != 2:
        raise template.TemplateSyntaxError, "%r takes one argument (the image location)" % token.contents.split()[0]
    else:
        return ExternalImageNode(template.Variable(args[1]))

class ExternalImageNode(template.Node):
    """
    Takes the form {% external_image url %} and renders as a URL pointing at
    the given image resized to match the device's max_image_width.
    """
    
    def __init__(self, url):
        self.url = url
        
    def render(self, context):
        url, width = self.url.resolve(context), context['device'].max_image_width

        ei, created = ExternalImage.objects.get_or_create(url=url)
        
        request = AnyMethodRequest(url, method='HEAD')
        response = urllib2.urlopen(request)

        # Check whether the image has changed since last we looked at it        
        if response.headers['ETag'] != ei.etag:

            # Can't use the shorter EIS.objects.filter(...).delete() as that
            # doesn't call the delete() method on individual objects, resulting
            # in the old images not being deleted.
            for eis in ExternalImageSized.objects.filter(external_image=ei):
                eis.delete()
            ei.etag = response.headers['Etag']
            ei.save()
        
        eis, created = ExternalImageSized.objects.get_or_create(external_image=ei, width=width)

        return eis.get_absolute_url()