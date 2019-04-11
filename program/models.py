#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from util.models import BaseModel


# 程序表
class Program(BaseModel):
    program_id = models.CharField(_('program_id'), max_length=16, unique=True, null=True, blank=False)
    program_name = models.CharField(_('program_name'), max_length=24, unique=True, null=True, blank=False)
    program_type = models.CharField(_('program_type'), max_length=24, blank=False, null=True,
                                    choices=(('filter', '过滤器'), ('organizer', '组织器')))
    program_user = models.ForeignKey('users.User', verbose_name=_('user'), on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = _('program')
        verbose_name_plural = _('program')
        ordering = ['-program_id']
        db_table = 'boss_program'

    def __str__(self):
        return self.program_name
