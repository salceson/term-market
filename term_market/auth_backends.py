from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


class IIETOAuthBackend(ModelBackend):
    def authenticate(self, oauth):
        if not oauth:
            return
        user = None

        UserModel = get_user_model()

        data = {}
        for data_uri in settings.OAUTH_DATA_URI:
            r = oauth.get(data_uri)
            data.update(r.json())

        query = Q(internal_id=data['user_id'])
        if 'transcript_number' in data:
            query |= Q(transcript_no=str(data['transcript_number']))
        try:
            user = UserModel.objects.get(query)
        except UserModel.DoesNotExist:
            user = UserModel()
        for oauth_data_key, user_model_attr in settings.OAUTH_DATA_TO_MODEL_MAPPING:
            setattr(user, user_model_attr, data.get(oauth_data_key))

        if user:
            user.save()

        return user
