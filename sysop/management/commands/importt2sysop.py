from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.auth.models import User
from sysop.models import Rotate, Server

import MySQLdb


YES_NULL = {
    '':    False,
    None:  False,
    'YES': True,
}


CARDINAL_COEF = {
    'N': 1,
    'S': -1,
    'E': 1,
    'W': -1,
}


ROTATES = {
    'excl': None,
}
for key in ('asia', 'aunz', 'china', 'euro', 'fire', 'germany', 'hungary', \
    'japan', 'noam', 'nordic', 'soam', 'swiss'):
    try:
        ROTATES[key] = Rotate.objects.get(dns_name=key)
    except:
        print key
        raise


class Command(BaseCommand):
    args = '<dbname> <dbuser> <dbpassword>'
    help = 'Migrates the old T2SYSOP database into django.'

    def handle(self, *args, **options):
        self.db = MySQLdb.connect(
            host="localhost",
            user=args[1],
            passwd=args[2],
            db=args[0])

        self.migrate_users()
        self.migrate_t2servers("t2servers")
        self.migrate_t2servers("deletedt2servers", deleted=True)
        self.migrate_t2servers("suspendedt2servers", out_of_service=True)

    @transaction.commit_on_success
    def migrate_t2servers(self, table, deleted=False, out_of_service=False):
        fields = (
            "id",
            "owner_id",
            "country",
            "city",
            "server_id",
            "dns_name",
            "ipv4",
            "ipv6",
            "regional",
            "regional2",
            "latitude",
            "longitude",
            "connection_desc",
            "connection_speed",
            "site_desc",
            "email_alerts",
        )

        cur = self.db.cursor()

        cur.execute("""SELECT `ID`, `UserNameID`, `T2Country`, `T2City`,
            `T2ServerName`, `T2DNSName`, `IPV4`, `IPV6`, `Regional`,
            `Regional2`, `T2lat`, `T2lon`, `ConnectionType`, `ConnectionSpeed`,
            `ServerLocationType`, `NagiosEmail` FROM %s""" % table)
        for row in cur.fetchall():
            old = dict(zip(fields, row))

            old['city'] = unicode(old['city'], 'latin-1')
            old['email_alerts'] = YES_NULL[old['email_alerts']]

            if old['ipv6'] == "NA":
                old['ipv6'] = None

            # one sysop used , instead of . to indicate decimal
            old['latitude'] = old['latitude'].replace(',', '.')
            old['longitude'] = old['longitude'].replace(',', '.')

            if len(old['longitude'].split('.')) > 2:
                # drop coordinates that don't make sense
                del old['latitude']
                del old['longitude']
            else:
                if ' ' in old['latitude']:
                    latitude, cardinal = old['latitude'].strip().split()
                    try:
                        old['latitude'] = abs(float(latitude)) * CARDINAL_COEF[cardinal]
                    except:
                        print old
                        raise

                if ' ' in old['longitude']:
                    longitude, cardinal = old['longitude'].strip().split()
                    old['longitude'] = abs(float(longitude)) * CARDINAL_COEF[cardinal]

            rotates = [ROTATES[k] for k in (old['regional'], old['regional2'])]

            for key in ('regional', 'regional2'):
                del old[key]

            old['deleted'] = deleted
            old['out_of_service'] = out_of_service

            server = Server(**old)
            server.save()

            server.rotate_set = filter(None, rotates)

    @transaction.commit_on_success
    def migrate_users(self):
        fields = (
            "id",
            "username",
            "password",
            "first_name",
            "seclevel",
            "email",
            "homepage",
            "callsign",
            "aprs2email",
        )

        cur = self.db.cursor()
        
        cur.execute("SELECT * FROM sysops")
        for row in cur.fetchall():
            olduser = dict(zip(fields, row))

            if olduser['id'] == 1:
                continue

            olduser['first_name'] = unicode(olduser['first_name'], 'latin-1')
            olduser['is_superuser'] = \
            olduser['is_staff'] = int(olduser['seclevel']) == 2
            if olduser['email'] is None:
                olduser['email'] = ''

            del olduser['seclevel']
            del olduser['homepage']
            del olduser['callsign']
            del olduser['aprs2email']

            user = User(**olduser)
            user.save()
