import os
import sys
import time
import boto
import datetime
from boto.s3.key import Key
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

CHUNK_DIR = '/tmp/chunk_dir'
os.path.exists(CHUNK_DIR) or os.mkdir(CHUNK_DIR)


class Command(BaseCommand):
    help = 'Back up the database to an archive on Amazon S3'

    def split_file(self, input_file, chunk_size=900000000):
        file_size = os.path.getsize(input_file)
        f = open(input_file, 'rb')
        data = f.read()
        f.close()

        if not os.path.exists(CHUNK_DIR):
            os.makedirs(CHUNK_DIR)

        bytes = len(data)
        num_chunks = bytes  / chunk_size
        if(bytes%chunk_size):
            num_chunks  += 1

        chunk_names = []
        for i in range(0, bytes + 1, chunk_size):
            chunk_name = "chunk%s" % i
            chunk_names.append(chunk_name)
            f = open(CHUNK_DIR+'/'+chunk_name, 'wb')
            f.write(data[i:i+chunk_size])
            f.close()

    def set_options(self, *args, **kwargs):
        """
        Initialize all the settings we'll use to backup the database.
        """
        # Set the database credentials
        self.db_user = settings.DATABASES['default']['USER']
        self.db_name = settings.DATABASES['default']['NAME']
        self.db_pass = settings.DATABASES['default']['PASSWORD']
        os.environ['PGPASSWORD'] = self.db_pass

        # Set up the file name
        if settings.PRODUCTION:
            prefix = 'prod'
        else:
            prefix = 'dev'
        now = time.strftime('%Y-%m-%d')
        self.filename = '%s_%s.sql.gz' % (prefix, now)
        self.cmd = 'pg_dump -U %s -Fc %s > %s' % (
            self.db_user,
            self.db_name,
            self.filename
        )

        # Set up everything we need on S3
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
        self.latest_key_path = self.key_path.replace(now, "latest")

    def handle(self, *args, **options):
        # Initialize all the settings we'll need
        self.set_options(*args, **options)

        # Create the backup locally
        print 'Backing up PostgreSQL: %s' % self.cmd
        os.system(self.cmd)

        # Upload it to S3 in pieces
        print "Uploading to %s" % self.key_path
        mp = self.bucket.initiate_multipart_upload(
            self.key_path,
            reduced_redundancy=False,
            policy='bucket-owner-full-control'
        )
        self.split_file(self.filename)
        file_list = os.listdir(CHUNK_DIR)
        i = 1
        for file_part in file_list:
            with open(CHUNK_DIR+'/'+file_part) as f:
                mp.upload_part_from_file(f, i)
            os.remove(CHUNK_DIR+'/'+file_part)
            i += 1
        mp.complete_upload()

        # Create a 'latest' copy and make both public
        print "Copying as %s" % self.latest_key_path
        key = self.bucket.lookup(mp.key_name)
        copy = key.copy(self.bucket, self.latest_key_path)

        # Delete the local file
        print "Deleting %s" % self.filename
        os.remove(self.filename)
