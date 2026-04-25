import os

from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def ensure_default_superuser(sender, **kwargs):
    username = os.environ.get('ADMIN_USERNAME', 'Nagebaba08')
    email = os.environ.get('ADMIN_EMAIL', 'admin@nagebaba.com')
    password = os.environ.get('ADMIN_PASSWORD', 'M@hesh@9405')

    if not all([username, email, password]):
        return

    User = get_user_model()
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)
