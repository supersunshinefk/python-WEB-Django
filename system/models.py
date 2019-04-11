#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _


# 执行记录
class ActionRecord(models.Model):
    action_data_time = models.DateTimeField(_('action_data_time'), auto_now_add=True)
    action_assigner = models.CharField(_('action_assigner'), max_length=64)
    action_reference = models.CharField(_('action_reference'), max_length=64, blank=True, null=True)
    action_record = models.CharField(_('action_record'), max_length=128, blank=True, null=True)

    class Meta:
        verbose_name = _('action_record')
        verbose_name_plural = _('action_record')
        ordering = ['-action_data_time']
        db_table = 'boss_action_record'


# 日志
class Log(models.Model):
    log_data_time = models.DateTimeField(_('log_data_time'), auto_now_add=True)
    log_assigner = models.CharField(_('log_assigner'), max_length=64)
    log_reference = models.CharField(_('log_reference'), max_length=64, blank=True, null=True)
    log_record = models.CharField(_('log_record'), max_length=128, blank=True, null=True)

    class Meta:
        verbose_name = _('log')
        verbose_name_plural = _('log')
        ordering = ['-log_data_time']
        db_table = 'boss_log'


# 输出消息记录
class Message(models.Model):
    message_data_time = models.DateTimeField(_('message_data_time'), auto_now_add=True)
    message_assigner = models.CharField(_('message_assigner'), max_length=64)
    message_reference = models.CharField(_('message_reference'), max_length=64, blank=True, null=True)
    message_record = models.CharField(_('message_record'), max_length=128, blank=True, null=True)

    class Meta:
        verbose_name = _('message')
        verbose_name_plural = _('message')
        ordering = ['-message_data_time']
        db_table = 'boss_message'
