#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from util.models import BaseModel


# 提示消息
class MessageOut(BaseModel):
    msg_out_id = models.CharField(_('msg_out_id'), max_length=16, unique=True)
    msg_out_name = models.CharField(_('msg_out_name'), max_length=24, unique=True)
    msg_out_user = models.ForeignKey('users.User', verbose_name=_('user'), on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = _('message_out')
        verbose_name_plural = _('messages_out')
        ordering = ['-msg_out_id']
        db_table = 'boss_message_out'

    def __str__(self):
        return self.msg_out_name
