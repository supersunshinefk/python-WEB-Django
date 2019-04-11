from django.db import models
from django.utils.translation import ugettext_lazy as _


class BaseModel(models.Model):
    """为模型类补充字段"""
    script = models.TextField(_('script'), max_length=2048, blank=True, null=True)
    version = models.CharField(_('version'), max_length=10, blank=True, null=True)
    remark = models.TextField(_('remark'), max_length=2048, blank=True, null=True)
    template = models.TextField(_('template'), max_length=2048, blank=True, null=True)
    is_available = models.BooleanField(_('is_available'), default=1)
    reference = models.CharField(_('reference'), max_length=64, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    data_updated = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        abstract = True
