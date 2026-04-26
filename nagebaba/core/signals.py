import os

from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def ensure_default_superuser(sender, **kwargs):
    username = os.environ.get('ADMIN_USERNAME')
    email = os.environ.get('ADMIN_EMAIL')
    password = os.environ.get('ADMIN_PASSWORD')

    if not all([username, email, password]):
        return

    User = get_user_model()
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'is_staff': True,
            'is_superuser': True,
        }
    )

    changed = created
    if user.email != email:
        user.email = email
        changed = True
    if not user.is_staff:
        user.is_staff = True
        changed = True
    if not user.is_superuser:
        user.is_superuser = True
        changed = True
    if not user.check_password(password):
        user.set_password(password)
        changed = True

    if changed:
        user.save()
