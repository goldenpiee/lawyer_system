import os
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Creates a superuser non-interactively using environment variables.'

    def handle(self, *args, **options):
        User = get_user_model()
        
        if User.USERNAME_FIELD != 'email':
             raise CommandError('USERNAME_FIELD must be email.')
             
        env_vars = {
            'email': os.environ.get('DJANGO_SUPERUSER_EMAIL'),
            'password': os.environ.get('DJANGO_SUPERUSER_PASSWORD'),
            'full_name': os.environ.get('DJANGO_SUPERUSER_FULL_NAME'),
            'phone': os.environ.get('DJANGO_SUPERUSER_PHONE'),
        }
        
        missing = [k for k, v in env_vars.items() if not v]
        if missing:
            raise CommandError(f'Missing environment variables: {", ".join(missing)}')

        if User.objects.filter(email=env_vars['email']).exists():
            self.stdout.write(self.style.SUCCESS('Superuser already exists.'))
            return 

        try:
            User.objects.create_superuser(**env_vars)
            self.stdout.write(self.style.SUCCESS(f"Superuser {env_vars['email']} created."))
        except Exception as e:
            raise CommandError(f'Failed to create superuser: {e}')