#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from util.models import BaseModel


# 数据分析项目
class AnalyticProject(BaseModel):
    project_id = models.CharField(_('project_id'), max_length=32, unique=True)
    project_name = models.CharField(_('project_name'), max_length=32, null=True)
    project_account = models.ForeignKey('account.Account', verbose_name=_('project_account'),
                                        on_delete=models.CASCADE, null=True)
    project_start_from = models.DateField(_('project_start_from'), null=True)
    project_end_by = models.DateField(_('project_end_by'), null=True)
    enable_time = models.DateTimeField(_('date_created'), null=True)
    project_source = models.ForeignKey('source.DataSource', verbose_name=_('project_source'),
                                       on_delete=models.CASCADE, null=True)
    project_pipe = models.ForeignKey('source.DataPipe', verbose_name=_('project_pipe'),
                                     on_delete=models.CASCADE, null=True)
    project_filter = models.ForeignKey('preprocess.DataFilter', verbose_name=_('project_filter'),
                                       on_delete=models.CASCADE, null=True)
    project_organizer = models.ForeignKey('preprocess.DataOrganizer', verbose_name=_('project_organizer'),
                                          on_delete=models.CASCADE, null=True)
    project_obj_group = models.ForeignKey('object.ObjectGroup', verbose_name=_('project_obj_group'),
                                          on_delete=models.CASCADE, null=True)
    project_ana_para = models.ForeignKey('parameter.AnalysisParameter', verbose_name=_('project_ana_para'),
                                         on_delete=models.CASCADE, null=True)
    project_opt_para = models.ForeignKey('parameter.OptimizationParameter', verbose_name=_('project_opt_para'),
                                         on_delete=models.CASCADE, null=True)
    project_dashboard = models.ForeignKey('output.Dashboard', verbose_name=_('project_dashboard'),
                                          on_delete=models.CASCADE, null=True)
    project_msg_out = models.ForeignKey('message.MessageOut', verbose_name=_('project_msg_out'),
                                        on_delete=models.CASCADE, null=True)
    project_rate = models.ForeignKey('account.ServiceRate', verbose_name=_('project_rate'),
                                     on_delete=models.CASCADE, null=True)
    # 为系统自带的自增id
    object_id = models.IntegerField(_('object_id'), null=True)
    project_user = models.ForeignKey('users.User', verbose_name=_('user'), on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = _('analytic_project')
        verbose_name_plural = _('analytic_project')
        ordering = ['-project_id']
        db_table = 'boss_analytic_project'

    def __str__(self):
        return self.project_name
