from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings
from util import constants
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from util.models import BaseModel


class User(AbstractUser, BaseModel):
    telephone = models.CharField(max_length=256, verbose_name="user_telephone", null=True)
    address = models.CharField(max_length=256, verbose_name="user_address", null=True)
    remark = models.TextField(_('remark'), max_length=2048, blank=True, null=True)

    class Meta:
        db_table = "df_users"

    def generate_token(self, user_id, username):
        s = Serializer(settings.SECRET_KEY, constants.USER_TOKEN_EXPIRES)
        data = {"user_id": user_id, "username": username}
        token = s.dumps(data)
        return token.decode()
