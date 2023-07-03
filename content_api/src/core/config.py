from logging import config as logging_config
from pydantic import BaseSettings, Field

from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    PROJECT_NAME: str = Field(..., env='PROJECT_NAME')
    REDIS_HOST: str = Field(..., env='REDIS_HOST')
    REDIS_PORT: int = Field(..., env='REDIS_PORT')
    ELASTIC_HOST: str = Field(..., env='ELASTIC_HOST')
    ELASTIC_PORT: int = Field(..., env='ELASTIC_PORT')
    HOST: str = Field(..., env='HOST')
    PORT: int = Field(..., env='PORT')
    CACHE_EXPIRE_IN_SECONDS: int = Field(..., env='CACHE_EXPIRE_IN_SECONDS')

    class Config:
        env_file = '.env'


settings = Settings()

SORT_DESC = "Сортировка. По умолчанию по возрастанию." \
            "'-' в начале - по убыванию."
SEARCH_DESC = "Поиск по названию"
PAGE_DESC = "Номер страницы"
PAGE_ALIAS = "page_number"
SIZE_DESC = "Количество элементов на странице"
SIZE_ALIAS = "page_size"
GENRE_DESC = "Жанр фильма"
