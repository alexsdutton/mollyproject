from datetime import datetime, time
from django.contrib.gis.db import models

PRESSURE_STATE_CHOICES = (
    ('+', 'rising'),
    ('-', 'falling'),
    ('~', 'steady'),
    ('c', 'no change'),
)

VISIBILITY_CHOICES = (
    ('vp', 'very poor'),
    ('p',  'poor'),
    ('vg', 'very good'),
    ('g', 'good'),
    ('df', 'dense fog'),
    ('f', 'fog'),
    ('e', 'excellent'),
    ('m', 'moderate'),
)

OUTLOOK_CHOICES = (
    ('si', 'sunny intervals'),
    ('gc', 'grey cloud'),
    ('hr', 'heavy rain'),
    ('s', 'sunny'),
    ('lr', 'light rain'),
    ('pc', 'partly cloudy'),
    ('f', 'fog'),
    ('wc', 'white cloud'),
    ('tst', 'thunder storm'),
    ('m', 'mist'),
    ('tsh', 'thundery shower'),
    ('lrs', 'light rain shower'),
    ('cs', 'clear sky'),
    ('d', 'drizzle'),
    ('h', 'hail'),
    ('lsn', 'light snow'),
    ('sn', 'snow'),
    ('hsn', 'heavy snow'),
)

OUTLOOK_TO_ICON = {
    'si':  'cloudy2',
    'gc':  'overcast',
    'hr':  'shower3',
    's':   'sunny',
    'lr':  'light_rain',
    'pc':  'cloudy3%(night)s',
    'f':   'fog%(night)s',
    'wc':  'cloudy5',
    'tst': 'tstorm1',
    'm':   'mist%(night)s',
    'tsh': 'tstorm3',
    'lrs': 'shower2%(night)s',
    'cs':  'sunny%(night)s',
    'd':   'shower1%(night)s',
    'h':   'hail',
    'lsn': 'snow1%(night)s',
    'sn':  'snow3%(night)s',
    'hsn': 'snow5',
}

class Weather(models.Model):
    bbc_id = models.PositiveIntegerField()
    name = models.TextField(null=True)

    outlook = models.CharField(null=True, max_length=3, choices=OUTLOOK_CHOICES)
    
    published_date = models.DateTimeField(null=True)
    observed_date = models.DateTimeField(null=True)
    modified_date = models.DateTimeField(auto_now=True)   
    
    temperature = models.IntegerField(null=True)
    wind_direction = models.CharField(null=True, max_length=2)
    wind_speed = models.IntegerField(null=True)
    humidity = models.IntegerField(null=True)
    pressure = models.PositiveIntegerField(null=True)
    pressure_state = models.CharField(null=True, max_length=1, choices=PRESSURE_STATE_CHOICES)
    visibility = models.CharField(null=True, max_length=2, choices=VISIBILITY_CHOICES)
    
    location = models.PointField(srid=4326, null=True)
    
    def icon(self):
        now = datetime.now().time()
        if now > time(7) or now > time(21):
            night = '_night'
        else:
            night = '' 
        return OUTLOOK_TO_ICON.get(self.outlook, 'dunno') % {'night':night}