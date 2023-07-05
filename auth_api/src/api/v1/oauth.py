from fastapi.responses import RedirectResponse
from fastapi import APIRouter, status

from fastapi import APIRouter, status
from fastapi.responses import RedirectResponse

from services.database import DbDep, CacheDep
from services.oauth import get_service_instance
from services.users import login_for_access_token

router = APIRouter()


@router.get('/signup/{service_name}',
            response_class=RedirectResponse,
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            description="Получение кода подтверждения из URL",
            response_description=
                        "Яндекс OAuth перенаправляет пользователя в приложение"
                        " на адрес, указанный в поле Redirect URI при "
                        "регистрации приложения.")
async def authorize(service_name: str) -> RedirectResponse:
    service = get_service_instance(service_name)
    response = service.authorize()
    return response


@router.get('/redirect/{service_name}',
            #response_class=RedirectResponse,
            #status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            description="Redirect URI, указанный при регистрации приложения.",
            response_description="code: Код подтверждения возвращается в URL"
                                 " перенаправления.")
async def redirect_oauth(service_name: str,
                         code: int,
                         db: DbDep,
                         cache: CacheDep):
    service = get_service_instance(service_name)
    user_info = service.get_user_info(code)
    user = await service.register(user_info, db)
    tokens = await login_for_access_token(db=db, cache=cache, form_data=user)
    return tokens
