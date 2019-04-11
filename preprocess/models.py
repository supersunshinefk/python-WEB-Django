#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from util.models import BaseModel


# 数据过滤器
class DataFilter(BaseModel):
    filter_id = models.CharField(_('filter_id'), max_length=32, unique=True)
    filter_name = models.CharField(_('filter_name'), max_length=32, null=True)
    filter_user = models.ForeignKey('users.User', verbose_name=_('user'), on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = _('data_filter')
        verbose_name_plural = _('data_filter')
        ordering = ['-filter_id']
        db_table = 'boss_data_filter'

    def __str__(self):
        return self.filter_name


# 数据组织器
class DataOrganizer(BaseModel):
    organizer_id = models.CharField(_('organizer_id'), max_length=32, unique=True)
    organizer_name = models.CharField(_('organizer_name'), max_length=32, null=True)
    organizer_user = models.ForeignKey('users.User', verbose_name=_('user'), on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = _('data_organizer')
        verbose_name_plural = _('data_organizer')
        ordering = ['-organizer_id']
        db_table = 'boss_data_organizer'

    def __str__(self):
        return self.organizer_name
