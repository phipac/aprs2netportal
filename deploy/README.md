# Installation instructions for aprs2netportal
These commands should work on Ubuntu, and likely Debian too. I apologize for not
writing automation for this.

# Install System Dependencies
    sudo apt-get install nginx python-pip python-virtualenv python-dev git-core libpq-dev postgresql postfix
    sudo pip install uwsgi

Note from [Django docs](https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/uwsgi/):
> Some distributions, including Debian and Ubuntu, ship an outdated version of
uWSGI that does not conform to the WSGI specification. Versions prior to 1.2.6
do not call `close` on the response object after handling a request. In those
cases the `request_finished` signal isn’t sent. This can result in idle
connections to database and memcache servers.

This is why I use pip to install uwsgi.

# Create user for portal
    sudo adduser portal
The uwsgi server will run under this user.

# Download Portal Software
    cd /var/www
    sudo git clone https://github.com/kd7lxl/aprs2netportal.git
    sudo git clone https://github.com/HamWAN/django-ssl-client-auth.git
    sudo chown portal:portal -R aprs2netportal django-ssl-client-auth

    sudo -s -u portal
    cd aprs2netportal
    ln -s /var/www/django-ssl-client-auth/django_ssl_auth .

# Set up Python environment
    portal@t2dev:/var/www/aprs2netportal$ virtualenv env
    portal@t2dev:/var/www/aprs2netportal$ source env/bin/activate
    (env)portal@t2dev:/var/www/aprs2netportal$

# Install Python Dependencies
    (env)portal@t2dev:/var/www/aprs2netportal$ pip install Django==1.6 south psycopg2
Make sure to activate the virutalenv before running pip.

# Database
## Set up PostgreSQL
    sudo -i -u postgres
    createuser portal
    createdb portal
    exit

Edit `aprs2netportal/settings.py` to point to new database. Postgres uses the system user
"portal" for authentication, so no password is needed.

## Initialize Database
    (env)portal@t2dev:/var/www/aprs2netportal$ ./manage.py syncdb
    (env)portal@t2dev:/var/www/aprs2netportal$ ./manage.py migrate

If you have a database backup, now would be a good time to import it.

# Test Django
    (env)portal@t2dev:/var/www/aprs2netportal$ ./manage.py runserver 0.0.0.0:8000

Any errors reported?

View in browser: http://t2dev.aprs2.net:8000/

If it’s working, continue on to configure uwsgi and nginx. We don’t want to run the test server forever.

# Configure uwsgi
Edit paths and UID/GID in `uwsgi.ini` if necessary.

    sudo cp ./deploy/uwsgi.conf /etc/init/
    sudo mkdir -p /var/log/uwsgi
    sudo touch /var/log/uwsgi/portal.log
    sudo chown portal:portal /var/log/uwsgi/portal.log
    sudo service uwsgi start

# Configure nginx
    sudo cp ./deploy/portal_nginx.conf /etc/nginx/sites-available/portal.conf
    sudo ln -s /etc/nginx/sites-available/portal.conf /etc/nginx/sites-enabled/
Edit paths in `/etc/nginx/sites-available/portal.conf` if necessary.

    sudo service nginx restart
