import http

import requests
from fastapi import HTTPException, Request, status as st
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

import core.config as conf


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> str:
        """
        Returns access token for request taken from header Authorization
        :param request:
        :return:
        """
        creds: HTTPAuthorizationCredentials = await super().__call__(request)
        if not creds:
            raise HTTPException(status_code=http.HTTPStatus.FORBIDDEN,
                                detail='Invalid authorization code.')
        if not creds.scheme == 'Bearer':
            raise HTTPException(status_code=http.HTTPStatus.UNAUTHORIZED,
                                detail='Only Bearer token might be accepted')
        return creds.credentials


security_jwt = JWTBearer()


async def check_roles(token: str, roles: str) -> None:
    try:
        status = requests.post(
            url=f'http://{conf.settings.host_auth}:'
                f'{conf.settings.port_auth}'
                f'/api/v1/users/check_roles',
            json={
                    'roles': f'{roles}'
                },
            headers={'Authorization': f'Bearer {token}'},
            )
    except requests.exceptions.Timeout as err:
        raise HTTPException(status_code=st.HTTP_504_GATEWAY_TIMEOUT,
                            detail=err.strerror)
    except requests.exceptions.TooManyRedirects as err:
        raise HTTPException(status_code=st.HTTP_502_BAD_GATEWAY,
                            detail=err.strerror)
    except requests.exceptions.RequestException as err:
        raise HTTPException(status_code=st.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=err.strerror)

    if not status:
        raise HTTPException(
            status_code=status.status_code,
            detail=status.json(),
            headers={"WWW-Authenticate": "Bearer"},
        )
