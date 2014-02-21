from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from countries import ISO3166


domain_validator = RegexValidator(
    regex=r'^(?=^.{4,253}$)(^((?!-)[a-zA-Z0-9-]{1,63}(?<!-)\.)+[a-zA-Z]{2,63}$)$',
)
hostname_validator = RegexValidator(
    regex=r'^(?![0-9]+$)(?!-)[a-zA-Z0-9-]{,63}(?<!-)$',
    message="Only lowercase letters and numbers are allowed.",
)


class Domain(models.Model):
    """APRS server domain, e.g., aprs.net, aprs2.net, firenet.us"""
    domain = models.CharField(max_length=253, validators=[domain_validator])

    def __unicode__(self):
        return self.domain

    class Meta:
        ordering = ['domain']


class Server(models.Model):
    """Tier 2 servers and hubs"""
    #FIXME: Should hubs be differentiated from servers?

    # Admin fields:
    owner = models.ForeignKey('auth.User', null=True, blank=True,
        related_name="servers_owned")
    server_id = models.CharField(max_length=20, null=True, blank=True,
        help_text="Polled from server")
    hostname = models.CharField(max_length=63, validators=[hostname_validator],
        help_text="Admin only")
    domain = models.ForeignKey(Domain)
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
        return self.server_id or self.hostname

    def disabled(self):
        return self.deleted or self.out_of_service

    def fqdn(self):
        return '.'.join((self.hostname, str(self.domain)))
    fqdn.short_description = "FQDN"

    def serialize(self):
        return (self.server_id, {
            'host': self.hostname,
            'ipv4': self.ipv4,
            'ipv6': self.ipv6,
            'disabled': self.disabled(),
        })

    def clean(self):
        # Don't allow saving a reserved name
        if ReservedHostname.objects.filter(hostname=self.hostname, domain=self.domain):
            raise ValidationError("%s is a reserved hostname." % self.fqdn())

        # Don't allow a server to have the same name as a rotate
        if Rotate.objects.filter(hostname=self.hostname, domain=self.domain):
            raise ValidationError("%s is a rotate." % self.fqdn())

    class Meta:
        ordering = ['server_id', 'hostname']


class Rotate(models.Model):
    """Primary and regional rotates."""
    hostname = models.CharField(max_length=63, validators=[hostname_validator])
    domain = models.ForeignKey(Domain)
    eligible = models.ManyToManyField(Server, blank=True)

    def __unicode__(self):
        return self.fqdn()

    def fqdn(self):
        return '.'.join((self.hostname, str(self.domain)))
    fqdn.short_description = "FQDN"

    def clean(self):
        # Don't allow saving a reserved name
        if ReservedHostname.objects.filter(hostname=self.hostname, domain=self.domain):
            raise ValidationError("%s is a reserved hostname." % self.fqdn())

        # Don't allow a rotate to have the same name as a server
        if Server.objects.filter(hostname=self.hostname, domain=self.domain):
            raise ValidationError("%s is a server." % self.fqdn())

    class Meta:
        ordering = ['hostname']


class ReservedHostname(models.Model):
    """Reserved hostnames, like ns1, used as a blacklist when naming servers"""
    hostname = models.CharField(max_length=63, validators=[hostname_validator])
    domain = models.ForeignKey(Domain)

    def __unicode__(self):
        return self.fqdn()

    def fqdn(self):
        return '.'.join((self.hostname, str(self.domain)))
    fqdn.short_description = "FQDN"

    class Meta:
        ordering = ['hostname', 'domain']
