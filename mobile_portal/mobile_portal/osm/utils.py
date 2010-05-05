try:
    import cPickle as pickle
except ImportError:
    import pickle
    
import hashlib, os, os.path
from datetime import datetime
from django.conf import settings
from django.db import IntegrityError
from models import GeneratedMap
from draw import get_map, get_fitted_map

MARKER_COLORS = (
    ('blue', '#0000ff', '#000050', '#ffffff'),
    ('red', '#ff0000', '#500000', '#ffffff'),
    ('yellow', '#f0ff00', '#4b5000', '#000000'),
    ('green', '#00ff1e', '#005009', '#000000'),
    ('purple', '#9146b8', '#3c1d4c', '#ffffff'),
    ('amber', '#ff7e00', '#824000', '#000000'),
)

MARKER_RANGE = xrange(1, 100)

def get_or_create_map(f, args):
    # This assumes that f is functional, i.e. its return value is determined
    # solely by it's arguments. In the case that a map is requested again
    # before the original map generation has finished, the following happens:
    # * Nothing has yet been saved to the database as we have to wait for the
    #   metadata to come back. Hence, we get a DoesNotExist.
    # * The map is regenerated. Due to the atomic nature of filesystem writes
    #   we can guarantee that we won't get a funnily spliced file written by
    #   the function f.
    # * The first call saves the GeneratedMap instance to the database.
    # * The second call attempts to do the same, but it would result in a
    #   duplicate primary key, and so it throws an IntegrityError.
    # * Due to the functional nature of f, we know we have the correct metadata
    #   for the map that has been generated, and that it will match that
    #   already stored in the database. As such, we can leave the database
    #   alone and return the metadata just generated.
    # Assuming that if we get a DoesNotExist that there won't be one by the
    # time we come to write leads to a race condition given the non-zero
    # duration of f. Subsequent attempts to get the map with that hash then
    # throws a MultipleObjectsReturned exception. Yes, this did happen. Seven
    # times, no less.
    hash = hashlib.sha224(pickle.dumps(repr(args))).hexdigest()[:16]
    
    try:
        gm = GeneratedMap.objects.get(hash=hash)
        gm.last_accessed = datetime.utcnow()
        gm.save()
        metadata = gm.metadata
    except GeneratedMap.DoesNotExist:
        if not os.path.exists(settings.GENERATED_MAP_DIR):
            os.makedirs(settings.GENERATED_MAP_DIR)
        metadata = f(filename=os.path.join(settings.GENERATED_MAP_DIR, hash), *args)
        gm = GeneratedMap(
            hash = hash,
            generated = datetime.utcnow(),
            last_accessed = datetime.utcnow(),
        )
        gm.metadata = metadata
        try:
            gm.save()
        except IntegrityError:
            pass

        if GeneratedMap.objects.all().count() > 5000:
            for gm in GeneratedMap.objects.order_by('last_accessed')[:50]:
                gm.delete()    
    
    return hash, metadata


def get_generated_map(points, width, height):
    return get_or_create_map(get_map, (points, width, height))
    
def fit_to_map(centre_point, points, min_points, zoom, width, height):
    points = list(points)
    return get_or_create_map(get_fitted_map, (centre_point, points, min_points, zoom, width, height))
