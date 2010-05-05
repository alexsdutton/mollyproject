from __future__ import division
import random, urllib, os, StringIO, PIL
from os.path import exists, join
import simplejson
from datetime import datetime, timedelta
from django.contrib.gis.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from mobile_portal.oxpoints.models import Entity
import django.dispatch

class RecentManager(models.Manager):
    def get_query_set(self):
        return super(RecentManager, self).get_query_set().filter(last_updated__gt = datetime.now() - timedelta(14))

class Placemarks(models.Model):
    "Cache for Google geocoding requests."
     
    _data = models.TextField(default='null')
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    query = models.TextField(blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    recent = RecentManager()
    objects = models.Manager()

    def get_data(self):
        if not hasattr(self, 'data_json'):
            self.data_json = simplejson.loads(self._data)
        return self.data_json
    def set_data(self, data):
        self.data_json = data
    data = property(get_data, set_data)
    
    def save(self, force_insert=False, force_update=False):
        self._data = simplejson.dumps(self.data)
        super(Placemarks, self).save()

feed_fetched = django.dispatch.Signal(providing_args=['category', 'url'])

class Feed(models.Model):
    """
    General cache for files retrieved from external sources.
    Use Feed.fetch(url, category, fetch_period, return_data) as opposed to
    creating Feed objects directly.
    """
    
    url = models.URLField()
    category = models.SlugField()
    fetch_period = models.PositiveIntegerField()
    last_fetched = models.DateTimeField(null=True)
    path = models.TextField(blank = True)
    auto_fetch = models.BooleanField()
    status = models.IntegerField()
    
    def __unicode__(self):
        return self.url
    
    def _fetch(self, fetch_period=None, return_data=False, raise_if_error=False):
        if not fetch_period is None:
            self.fetch_period = fetch_period
        if not self.path:
            while not self.path or exists(self.get_path()):
                self.path = "%08x" % random.randint(0, 16**8-1)
        b = self.last_fetched
        if not self.last_fetched or self.last_fetched + timedelta(0, self.fetch_period) < datetime.now():
            require_save = True
            a = self.get_path()
            f = open(self.get_path(), 'w')
            response = urllib.urlopen(self.url)
            data = response.read()
            self.status = response.code
            f.write(data)
            f.close()
            self.last_fetched = datetime.now()
            self.save()
            
            feed_fetched.send(sender=self, category=self.category, url=self.url)
            
            if return_data:
                if raise_if_error and self.status != 200:
                    raise IOError(self.status)
                return data
        elif return_data:
            if raise_if_error and self.status != 200:
                raise IOError(self.status)
            return self.get_data()
    
    def get_path(self):
        return join(settings.FEED_PATH, self.path)
        
    def get_data(self):
        a = self.get_path()
        return open(self.get_path(), 'r').read()
                
    @staticmethod
    def fetch(url, category=None, fetch_period=3600, return_data=False, raise_if_error=False):
        try:
            feed = Feed.objects.get(url=url)
        except Feed.DoesNotExist:
            feed = Feed(url=url, category=category, fetch_period=fetch_period, status=0)
            feed.save()
        
        return feed._fetch(fetch_period=fetch_period, return_data=return_data, raise_if_error=raise_if_error)
        
class Profile(models.Model):
    user = models.ForeignKey(User, unique=True)
    webauth_username = models.TextField(null=True, blank=True)
    display_name = models.TextField(null=True, blank=True)
    
    
    fireeagle_access_token = models.TextField(blank=True)
    fireeagle_access_secret = models.TextField(blank=True)
    
    location = models.PointField(null=True, srid=4326, blank=True)
    location_updated = models.DateTimeField(null=True, blank=True)
    
    def __unicode__(self):
        return self.user.username

LOCATION_ACCURACY_CHOICES = (
    (1, "Don't share my location"), 
    (2, 'Whether I am in Oxford'),
    (3, 'Locality within Oxford'),
    (4, 'Nearest college or department'),
    (5, 'Exact location'),
)

class LocationShareTimes(models.Model):
    user = models.ForeignKey(User)
    share_times = models.TextField()

class LocationShare(models.Model):
    from_user = models.ForeignKey(User, related_name='location_share_from')
    to_user = models.ForeignKey(User, related_name='location_share_to')
    
    accuracy = models.PositiveIntegerField(choices=LOCATION_ACCURACY_CHOICES, default=1)
    share_times = models.ForeignKey(LocationShareTimes, null=True, blank=True)
    until = models.DateTimeField(null=True, blank=True)
    
    location = models.PointField(srid=4326, null=True, blank=True)
    location_title = models.TextField(blank=True)
    location_entity = models.ForeignKey(Entity, null=True, blank=True)
    location_updated = models.DateTimeField(null=True)

class FrontPageLink(models.Model):
    slug = models.SlugField()
    title = models.TextField()
    urlconf_name = models.TextField()
    
    def __unicode__(self):
        return self.title
    
    @property
    def url(self):
        return reverse(self.urlconf_name)

class Config(models.Model):
    key = models.SlugField()
    value = models.TextField()
    
class ExternalImage(models.Model):
    url = models.URLField()
    etag = models.TextField(null=True)
    last_modified = models.TextField(null=True)
    last_updated = models.DateTimeField() # This one is in UTC
    width = models.PositiveIntegerField(null=True)
    height = models.PositiveIntegerField(null=True)
    
    def save(self, force_insert=False, force_update=False):
        self.last_updated = datetime.utcnow()
        super(ExternalImage, self).save(force_insert=False, force_update=False)
    
class ExternalImageSized(models.Model):
    external_image = models.ForeignKey(ExternalImage)
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    slug = models.SlugField()

    def get_filename(self):
        if not self.slug:
            while not self.slug or ExternalImageSized.objects.filter(slug=self.slug).count():
                self.slug = "%08x" % random.randint(0, 16**8-1)
        if not os.path.exists(settings.EXTERNAL_IMAGE_DIR):
            os.makedirs(settings.EXTERNAL_IMAGE_DIR)
        return os.path.join(settings.EXTERNAL_IMAGE_DIR, self.slug)

    def get_absolute_url(self):
        return reverse('external_image', args=[self.slug])    

    def save(self, force_insert=False, force_update=False):
        if not self.id:
            im = PIL.Image.open(StringIO.StringIO(urllib.urlopen(self.external_image.url).read()))
            
            size = im.size
            ratio = size[1] / size[0]
            
            if self.width >= size[0]:
                resized = im
            else:
                resized = im.resize((self.width, int(round(self.width*ratio))), PIL.Image.ANTIALIAS)
            self.width, self.height = resized.size

            try:            
                resized.save(self.get_filename(), format='jpeg')
            except IOError:
                resized.convert('RGB').save(self.get_filename(), format='jpeg')

            self.external_image.width = size[0]
            self.external_image.height = size[1]
            
        super(ExternalImageSized, self).save(force_insert=False, force_update=False)
  
    def delete(self):
        os.unlink(self.get_filename())
        super(ExternalImageSized, self).delete()

class UserMessage(models.Model):
    session_key = models.TextField()
    message = models.TextField()
    read = models.BooleanField(default=False)
    when = models.DateTimeField(auto_now_add=True)