from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile

class Command(BaseCommand):
    help = 'Create user profiles for existing users'

    def handle(self, *args, **kwargs):
        users = User.objects.filter(profile__isnull=True)
        count = 0
        for user in users:
            Profile.objects.create(user=user)
            count += 1
        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} user profiles'))