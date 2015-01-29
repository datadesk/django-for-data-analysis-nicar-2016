from django.utils.crypto import get_random_string
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Generates a secret key for use in project settings"

    def handle(self, *args, **options):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        key = get_random_string(50, chars)
        print 'SECRET_KEY = "%s"' % key
