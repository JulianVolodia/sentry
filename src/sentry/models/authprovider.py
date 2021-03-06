from __future__ import absolute_import, print_function

from django.db import models
from django.utils import timezone
from jsonfield import JSONField

from sentry.db.models import BoundedPositiveIntegerField, Model

from .organizationmember import OrganizationMember


_organizationemmber_type_field = OrganizationMember._meta.get_field('type')


class AuthProvider(Model):
    organization = models.ForeignKey('sentry.Organization', unique=True)
    provider = models.CharField(max_length=128)
    config = JSONField()

    date_added = models.DateTimeField(default=timezone.now)
    sync_time = BoundedPositiveIntegerField(null=True)
    last_sync = models.DateTimeField(null=True)

    default_role = BoundedPositiveIntegerField(
        choices=_organizationemmber_type_field.choices,
        default=_organizationemmber_type_field.default
    )
    default_global_access = models.BooleanField(default=True)
    default_teams = models.ManyToManyField('sentry.Team', blank=True)

    class Meta:
        app_label = 'sentry'
        db_table = 'sentry_authprovider'

    def get_provider(self):
        from sentry.auth import manager

        return manager.get(self.provider, **self.config)

    def get_audit_log_data(self):
        return {
            'provider': self.provider,
            'config': self.config,
            'default_Role': self.default_role,
        }
