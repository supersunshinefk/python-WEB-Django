#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from util.models import BaseModel


# 原始数据
class OriginalData(BaseModel):
    original_data_id = models.CharField(_('original_data_id'), max_length=16, unique=True, null=False, blank=False)
    original_data_name = models.CharField(_('original_data_name'), max_length=16, null=True, blank=False)
    project_id = models.CharField(_('project_id'), max_length=16, null=True, blank=False)
    data = models.TextField(_('data'), blank=True, null=True)
    original_data_user = models.ForeignKey('users.User', verbose_name=_('user'), on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = _('original_data')
        verbose_name_plural = _('original_data')
        ordering = ['-original_data_id']
        db_table = 'boss_original_data'

    def __str__(self):
        return self.original_data_name


# 格式化数据
class FormatData(BaseModel):
    format_data_id = models.CharField(_('format_data_id'), max_length=16, unique=True, null=False, blank=False)
    format_data_name = models.CharField(_('format_data_name'), max_length=16, null=True, blank=False)
    project_id = models.CharField(_('project_id'), max_length=16, null=True, blank=False)
    data = models.TextField(_('data'), blank=True, null=True)
    format_data_user = models.ForeignKey('users.User', verbose_name=_('user'), on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = _('format_data')
        verbose_name_plural = _('format_data')
        ordering = ['-format_data_id']
        db_table = 'boss_format_data'

    def __str__(self):
        return self.format_data_name


# 计算数据
class CalculateData(BaseModel):
    calculate_data_id = models.CharField(_('calculate_data_id'), max_length=16, unique=True, null=False, blank=False)
    calculate_data_name = models.CharField(_('calculate_data_name'), max_length=16, null=True, blank=False)
    project_id = models.CharField(_('project_id'), max_length=16, null=True, blank=False)
    data = models.TextField(_('data'), blank=True, null=True)
    calculate_data_user = models.ForeignKey('users.User', verbose_name=_('user'), on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = _('calculate_data')
        verbose_name_plural = _('calculate_data')
        ordering = ['-calculate_data_id']
        db_table = 'boss_calculate_data'

    def __str__(self):
        return self.calculate_data_name
