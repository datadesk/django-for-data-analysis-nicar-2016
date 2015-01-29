import os
import boto
from datetime import datetime
from datetime import timedelta
from django.conf import settings
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError


custom_options = (
    make_option(
        "--name",
        action="store",
        dest="name",
        default='',
        help="A custom name for the database we're creating locally"
    ),
    make_option(
        "--env",
        action="store",
        dest="env",
        default='prod',
        help="The deployment environment you want pull the database from. \
By default it's prod."
    ),
)


class Command(BaseCommand):
    args = '<date YYYY-MM-DD>'
    help = 'Load a database snapshot from our nightly archive. Pulls latest \
by default. Specify date for an older one.'
    option_list = BaseCommand.option_list + custom_options

    def set_options(self, *args, **kwargs):
        # If the user provides a date, try to use that
        if args:
            try:
                dt = datetime.strptime(args[0], '%Y-%m-%d')
                dt = dt.strftime("%Y-%m-%d")
            except ValueError:
                raise CommandError("The date you submitted is not valid.")
        # Otherwise just use the today minus one day
        else:
            dt = 'latest'
        self.filename = '%s_%s.sql.gz' % (kwargs['env'], dt)

        # Get all our S3 business straight
        self.bucket_name = settings.AWS_BACKUP_BUCKET_NAME
        self.boto_conn = boto.connect_s3(
            settings.AWS_ACCESS_KEY_ID,
            settings.AWS_SECRET_ACCESS_KEY
        )
        self.bucket = self.boto_conn.get_bucket(self.bucket_name)
        if hasattr(settings, 'AWS_BACKUP_BUCKET_DIRECTORY'):
            self.key_path = '%s/%s' % (
                settings.AWS_BACKUP_BUCKET_DIRECTORY,
                self.filename
            )
        else:
            self.key_path = self.filename

        # Set local database settings
        os.environ['PGPASSWORD'] = settings.DATABASES['default']['PASSWORD']
        self.db_user = settings.DATABASES['default']['USER']
        self.db_name = kwargs.get('name') or settings.DATABASES['default']['NAME']

    def handle(self, *args, **options): 
        # Initialize the options
        self.set_options(*args, **options)

        # Download the snapshot
        self.download(self.key_path)

        # Load the snapshot into the database
        self.load(self.filename)

    def load(self, source):
        """
        Load a database snapshot into our postgres installation.
        """
        print "Loading to new database: %s" % self.db_name
        # If the db already exists, we need to drop it.
        try:
            os.system("dropdb -U %s %s" % (self.db_user, self.db_name))
        except:
            pass
        # Create the database
        os.system("createdb -U %s %s" % (self.db_user, self.db_name))
        # Load the data
        os.system("pg_restore -U %s -Fc -d %s ./%s" % (
                self.db_user,
                self.db_name,
                source
            )
        )
        # Delete the snapshot
        os.system("rm ./%s" % source)

    def download(self, dt):
        """
        Download a database snapshot.
        """
        print "Downloading database: %s" % self.key_path
        self.key = self.bucket.get_key(self.key_path)
        if not self.key:
            raise CommandError("%s does not exist in the database archive." % (
                self.key_path
            ))
        self.key.get_contents_to_filename(self.filename)
