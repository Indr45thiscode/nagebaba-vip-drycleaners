import os

from django.apps import AppConfig
from django.db import connections
from django.db.utils import OperationalError, ProgrammingError


class CoreConfig(AppConfig):
    name = 'core'
    _admin_bootstrapped = False

    def ready(self):
        if CoreConfig._admin_bootstrapped:
            return

        username = os.environ.get('ADMIN_USERNAME', 'Nagebaba08')
        email = os.environ.get('ADMIN_EMAIL', 'admin@nagebaba.com')
        password = os.environ.get('ADMIN_PASSWORD', 'M@hesh@9405')

        if not all([username, email, password]):
            return

        try:
            connection = connections['default']
            tables = connection.introspection.table_names()
            if 'auth_user' not in tables:
                return

            from django.contrib.auth import get_user_model

            User = get_user_model()
            if not User.objects.filter(username=username).exists():
                User.objects.create_superuser(username=username, email=email, password=password)

            CoreConfig._admin_bootstrapped = True
        except (OperationalError, ProgrammingError):
            # Database may not be ready during build or initial migration.
            return
