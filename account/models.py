#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from util.models import BaseModel


class Account(BaseModel):
    account_id = models.CharField(_('account_id'), max_length=32, unique=True)
    account_name = models.CharField(_('account_name'), max_length=64, null=True)
    account_login = models.CharField(_('account_login'), max_length=32, null=True)
    account_pin = models.CharField(_('account_pin'), max_length=32, null=True)
    account_user = models.ForeignKey('users.User', verbose_name=_('user'), on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = _('account')
        verbose_name_plural = _('account')
        ordering = ['-account_id']
        db_table = 'boss_account'

    def __str__(self):
        return self.account_name


# 账单
class Bill(BaseModel):
    bill_number = models.CharField(_('bill_number'), max_length=32, unique=True)
    bill_memo = models.CharField(_('bill_memo'), max_length=32, null=True)
    biller = models.CharField(_('biller'), max_length=32, null=True)
    bill_account = models.ForeignKey('account', verbose_name=_('bill_account'), on_delete=models.CASCADE, null=True)
    bill_amount = models.DecimalField(_('bill_amount'), max_digits=12, decimal_places=2, null=True, default='0.00')
    bill_due = models.DateField(_('bill_due'), null=True)

    class Meta:
        verbose_name = _('bill')
        verbose_name_plural = _('bill')
        db_table = 'boss_bill'

    def __str__(self):
        return self.bill_memo


# 资费
class ServiceRate(BaseModel):
    rate_id = models.CharField(_('rate_id'), max_length=32, unique=True)
    rate_name = models.CharField(_('rate_name'), max_length=32, null=True)
    rate_per_project = models.IntegerField(_('rate_per_project'), default='0', null=True)
    rate_per_object = models.IntegerField(_('rate_per_object'), default='0', null=True)
    rate_cycle = models.CharField(_('rate_cycle'), max_length=32, null=True,
                                  choices=(('Y', '年'), ('M', '月'), ('W', '周'), ('d', '日')))

    class Meta:
        verbose_name = _('service_rate')
        verbose_name_plural = _('service_rate')
        ordering = ['-rate_id']
        db_table = 'boss_service_rate'

    def __str__(self):
        return self.rate_name
