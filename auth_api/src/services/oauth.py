import requests
from fastapi.responses import RedirectResponse

from core.config import yandex_config
from schemas.users import UserSignUpOAuth
from services.database import DbDep
from services.users import register_user


class YandexOauth:
    """Класс для работы с авторизацией яндекса."""
    def __init__(self):
        self.client_id = yandex_config.client_id
        self.secret = yandex_config.secret
        self.authorization_url = f'https://oauth.yandex.ru/authorize' \
                                 f'?response_type=code' \
                                 f'&client_id={self.client_id}' \
                                 f'&display=popup' \
                                 f'&scope=login:email login:info'

    def authorize(self):
        """Редирект на авторизацию в яндексе."""
        response = RedirectResponse(url=self.authorization_url)
        return response

    def get_tokens(self, code: str) -> dict[str, str]:
        """Получить токены от яндекса по коду."""
        return requests.post(
            url='https://oauth.yandex.ru/token',
            data={
                'grant_type': 'authorization_code',
                'client_id': self.client_id,
                'client_secret': self.secret,
                'code': code
            }
        ).json()

    def get_user_info(self, code: str) -> dict[str, str]:
        """Получить информацию о юзере яндекса по токенам."""
        tokens = self.get_tokens(code)
        return requests.get(
            url='https://login.yandex.ru/info?',
            headers={
                'Authorization': f'OAuth {tokens["access_token"]}',
            },
        ).json()

    @staticmethod
    async def register(user_info: dict, db: DbDep):
        res = await register_user(
            UserSignUpOAuth(email=user_info['default_email'],
                            first_name=user_info['first_name'],
                            last_name=user_info['last_name'],),
            db)
        return res


def get_service_instance(service_name: str):
    if service_name == 'yandex':
        return YandexOauth()
