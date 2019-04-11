#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from util.models import BaseModel


# 数据源
class DataSource(BaseModel):
    source_id = models.CharField(_('source_id'), max_length=32, unique=True)
    source_name = models.CharField(_('source_name'), max_length=32, null=True)
    source_mode = models.CharField(_('source_mode'), max_length=32, null=True,
                                   choices=(('G', 'GARDS'), ('NG', 'Non-GARDS')))
    source_user = models.ForeignKey('users.User', verbose_name=_('user'), on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = _('data_source')
        verbose_name_plural = _('data_source')
        ordering = ['-source_id']
        db_table = 'boss_data_source'

    def __str__(self):
        return self.source_name


# 数据管道
class DataPipe(BaseModel):
    pipe_id = models.CharField(_('pipe_id'), max_length=32, unique=True)
    pipe_name = models.CharField(_('pipe_name'), max_length=32, null=True)
    pipe_user = models.ForeignKey('users.User', verbose_name=_('user'), on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = _('data_pipe')
        verbose_name_plural = _('data_pipe')
        ordering = ['-pipe_id']
        db_table = 'boss_data_pipe'

    def __str__(self):
        return self.pipe_name
