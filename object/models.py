#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from util.models import BaseModel


# 分析对象组
class ObjectGroup(BaseModel):
    obj_group_id = models.CharField(_('obj_group_id'), max_length=32, unique=True)
    obj_group_name = models.CharField(_('obj_group_name'), max_length=32, null=True)
    object_category = models.CharField(_('object_category'), max_length=32, null=True,
                                       choices=(('C', _('compressor')), ('B', _('boiler')), ('E', _('engline')),
                                                ('G', _('generator'))))
    obj_group_user = models.ForeignKey('users.User', verbose_name=_('user'), on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = _('object_group')
        verbose_name_plural = _('object_group')
        ordering = ['-obj_group_id']
        db_table = 'boss_object_group'

    def __str__(self):
        return self.obj_group_name


# 分析对象
class Object(BaseModel):
    obj_group_id = models.ForeignKey('ObjectGroup', verbose_name=_('obj_group_id'), on_delete=models.CASCADE, null=True)
    object_id = models.CharField(_('object_id'), max_length=32, unique=True)
    object_reference_id = models.CharField(_('object_reference_id'), max_length=32, null=True)
    object_name = models.CharField(_('object_name'), max_length=32, null=True)
    object_model = models.CharField(_('object_model'), max_length=32, null=True)
    object_user = models.ForeignKey('users.User', verbose_name=_('user'), on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = _('object')
        verbose_name_plural = _('object')
        ordering = ['-object_id']
        db_table = 'boss_object'

    def __str__(self):
        return self.object_name
