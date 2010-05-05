from models import Preferences
from defaults import defaults

class PreferencesMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated():
            request.preferences_object, created = Preferences.objects.get_or_create(user=request.user)
        else:
            session_key = request.session.session_key
            if not 'prefs_stored' in request.session:
                request.session['prefs_stored'] = True
            request.preferences_object, created = Preferences.objects.get_or_create(session_key=session_key)
        request.preferences = request.preferences_object.preference_set

    def process_response(self, request, response):
        try:
            request.preferences_object.save()
        except AttributeError:
            pass

        return response