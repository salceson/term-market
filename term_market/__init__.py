# django.js monkey patch
# https://github.com/noirbizarre/django.js/issues/53
# settings not found in request context
try:
    from django.conf import settings
    from djangojs.context_serializer import ContextSerializer

    def _as_dict(self):
        data = self._as_dict()
        data.update({
            'STATIC_URL': settings.STATIC_URL,
            'MEDIA_URL': settings.MEDIA_URL,
            'LANGUAGES': settings.LANGUAGES,
            'LANGUAGE_CODE': settings.LANGUAGE_CODE,
        })
        return data

    ContextSerializer._as_dict = ContextSerializer.as_dict
    ContextSerializer.as_dict = _as_dict
except:
    pass

default_app_config = 'term_market.apps.TermMarketConfig'
