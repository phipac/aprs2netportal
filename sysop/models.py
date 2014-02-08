from django.db import models
from django.core.validators import RegexValidator

from countries import ISO3166


dns_validator = RegexValidator(
    regex=r'^(?![0-9]+$)(?!-)[a-zA-Z0-9-]{,63}(?<!-)$',
    message="Only lowercase letters and numbers are allowed.",
)


class Server(models.Model):
    """Tier 2 servers and hubs"""
    #FIXME: Should hubs be differentiated from servers?

    # Admin fields:
    owner = models.ForeignKey('auth.User', null=True, blank=True,
        related_name="servers_owned")
    server_id = models.CharField(max_length=20, null=True, blank=True,
        help_text="Polled from server")
    dns_name = models.CharField(max_length=63, verbose_name="DNS name",
        validators=[dns_validator], help_text="Admin only")
    deleted = models.BooleanField(blank=True)

    # Owner-editable fields:
    out_of_service = models.BooleanField(blank=True, help_text="Use this "
        "option to remove your server from DNS before planned maintenance.")
    ipv4 = models.GenericIPAddressField(protocol="IPv4", null=True, blank=True,
        verbose_name="IPv4")
    ipv6 = models.GenericIPAddressField(protocol="IPv6", null=True, blank=True,
        verbose_name="IPv6")
    #FIXME: is FloatField() appropriate for lat/lon?
    latitude = models.FloatField(null=True, blank=True, help_text="Decimal")
    longitude = models.FloatField(null=True, blank=True, help_text="Decimal")
    city = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True,
        choices=sorted(ISO3166.items(), key=lambda country: country[1]))
    connection_desc = models.CharField(max_length=255, null=True, blank=True,
        verbose_name="Connection description",
        help_text="ADSL, Fiber, E1, T1, 33.6 Modem, etc.")
    connection_speed = models.CharField(max_length=255, null=True, blank=True)
    site_desc = models.CharField(max_length=255, null=True, blank=True,
        verbose_name="Site description",
        help_text="Data Center, Home, etc.")
    email_alerts = models.BooleanField(blank=True)
    authorized_sysops = models.ManyToManyField('auth.User', blank=True,
        related_name="authorized_servers",
        help_text="Use this to allow other sysops to edit this server.")

    def __unicode__(self):
        return self.server_id or self.dns_name

    def disabled(self):
        return self.deleted or self.out_of_service

    def fqdn(self):
        return "%s.aprs2.net" % self.dns_name

    def serialize(self):
        return (self.server_id, {
            'host': self.dns_name,
            'ipv4': self.ipv4,
            'ipv6': self.ipv6,
            'disabled': self.disabled(),
        })

    class Meta:
        ordering = ['server_id', 'dns_name']


class Rotate(models.Model):
    """Primary and regional rotates."""
    dns_name = models.CharField(max_length=63, validators=[dns_validator])
    eligible = models.ManyToManyField(Server, blank=True)

    def __unicode__(self):
        return self.dns_name

    def fqdn(self):
        return "%s.aprs2.net" % self.dns_name

    class Meta:
        ordering = ['dns_name']