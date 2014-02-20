from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.auth.models import User

import MySQLdb


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

            print olduser
            # continue

            user = User(**olduser)
            user.save()
