#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from util.models import BaseModel


# 显示板
class Dashboard(BaseModel):
    dashboard_id = models.CharField(_('dashboard_id'), max_length=32, unique=True)
    dashboard_url = models.CharField(_('dashboard_url'), max_length=256, null=True)
    dashboard_account = models.ForeignKey('account.Account', verbose_name=_('dashboard_account'),
                                          on_delete=models.CASCADE, null=True)
    dashboard_project = models.CharField(_('dashboard_project'), max_length=32, blank=True, null=True)
    dashboard_user = models.ForeignKey('users.User', verbose_name=_('user'), on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = _('dashboard')
        verbose_name_plural = _('dashboard')
        ordering = ['-dashboard_id']
        db_table = 'boss_dashboard'

    def __str__(self):
        return self.dashboard_id
