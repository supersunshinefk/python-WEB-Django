#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from util.models import BaseModel


# 分析参数
class AnalysisParameter(BaseModel):
    ana_para_id = models.CharField(_('ana_para_id'), max_length=16, unique=True)
    ana_para_name = models.CharField(_('ana_para_name'), max_length=24, unique=True)
    object_id = models.ForeignKey('object.Object', verbose_name=_('object_id'),
                                  on_delete=models.CASCADE, null=True)
    analysis_user = models.ForeignKey('users.User', verbose_name=_('user'), on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = _('analysis_parameter')
        verbose_name_plural = _('analysis_parameter')
        ordering = ['-ana_para_id']
        db_table = 'boss_analysis_parameter'

    def __str__(self):
        return self.ana_para_name


# 优化参数
class OptimizationParameter(BaseModel):
    opt_para_id = models.CharField(_('opt_para_id'), max_length=16, unique=True)
    opt_para_name = models.CharField(_('opt_para_name'), max_length=24, unique=True)
    object_id = models.ForeignKey('object.Object', verbose_name=_('object_id'),
                                  on_delete=models.CASCADE, null=True)
    optimization_user = models.ForeignKey('users.User', verbose_name=_('user'), on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = _('optimization_parameter')
        verbose_name_plural = _('optimization_parameter')
        ordering = ['-opt_para_id']
        db_table = 'boss_optimization_parameter'

    def __str__(self):
        return self.opt_para_name
