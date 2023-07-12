import http
import json

import requests
# from django.config import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        django_login_roles = {'admin', 'manager'}
        url = "http://127.0.0.1/api/v1/auth/login-sso"
        payload = {'username': username, 'password': password}
        response = requests.post(url, json=payload)
        if response.status_code != http.HTTPStatus.OK:
            return None

        data = response.json()

        # try:
        user, created = User.objects.get_or_create(id=data['id'],)
        user.email = data.get('email')
        user.first_name = data.get('first_name')
        user.last_name = data.get('last_name')
        user.is_admin = False
        for django_role in django_login_roles:
            for user_role in data.get('roles'):
                if django_role in user_role:
                    user.is_admin = True
                    break
            else:
                continue
            break

        user.is_active = not data.get('disabled')
        user.save()

        # except Exception as e:
        #     print(e)
        #     return None

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
