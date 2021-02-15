import aiohttp
import asyncio
import json
import logging
import math
from urllib import parse as up
import datetime as dt
import enum
from typing import Any, Dict, List, Optional, Coroutine
from typing_extensions import Literal

from ..responses import relay_devices_instance as rdi
from ..responses import locations_instance as li
from ..responses import thresholds_instance as ti
from ..responses import me_instance as mi


_LOGGER = logging.getLogger(__name__)


class AirThingsConstant:
    CT_JSON = 'application/json'
    CT_USER_AGENT = 'Mozilla/5.0 Chrome/87.0'
    CT_BEARER_FORMAT = 'Bearer {0}'
    CT_ACCOUNTS_API_BASE = 'https://accounts-api.airthings.com/v1/{0}'
    CT_WEB_API_BASE = 'https://web-api.airthin.gs/v1/{0}'
    CT_ACCOUNTS_ORIGIN = 'https://accounts.airthings.com'
    CT_DASHBOARD_ORIGIN = 'https://dashboard.airthings.com'
    CT_DASHBOARD_SECRET = 'e333140d-4a85-4e3e-8cf2-bd0a6c710aaa'


@enum.unique
class AirThingsAuthenticationAdvise(enum.Enum):
    ShouldWait = 0
    ShouldLogin = 1
    ShouldRefreshToken = 2
    ShouldBeGood = 3
    ShouldCheckCredentials = 4


class AirThingsException(Exception):
    """Base exception for AirThings API errors."""

    def __init__(self, error_code: int, error_details: str) -> None:
        """Initialise AirThingsException."""
        self.error_code = error_code
        self.error_details = error_details


class AirThingsInvalidCredentialsException(Exception):
    """Highlevel Exception for AirThings invalid credentials errors."""
    pass


class AirThingsUnauthorizedException(AirThingsException):
    """Exception for AirThings API unauthorized errors."""
    pass


class AirThingsManager:

    def __init__(self, username: str, password: str, session: aiohttp.ClientSession) -> None:
        self.username = username
        self.password = password
        self.session = session
        self.tokens: Optional[Dict[str, Any]] = None

    async def get_relay_devices_instance(self) -> rdi.RelayDevicesInstance:
        return rdi.relay_devices_instance_from_dict(
            await self.__execute_poll(
                poll_coroutine=self.__poll_relay_devices()))

    async def get_locations_instance(self) -> li.LocationsInstance:
        return li.locations_instance_from_dict(
            await self.__execute_poll(
                poll_coroutine=self.__poll_locations()))

    async def get_thresholds_instance(self) -> ti.ThresholdsInstance:
        return ti.thresholds_instance_from_dict(
            await self.__execute_poll(
                poll_coroutine=self.__poll_thresholds()))

    async def get_me_instance(self) -> mi.MeInstance:
        return mi.me_instance_from_dict(
            await self.__execute_poll(
                poll_coroutine=self.__poll_me()))

    async def validate_credentials(self) -> bool:
        advise = await self.__assert_ready()
        return (advise == AirThingsAuthenticationAdvise.ShouldBeGood)
        
    async def __execute_poll(self, poll_coroutine: Coroutine) -> Optional[Dict[str, Any]]:
        advise = await self.__assert_ready()
        
        if advise == AirThingsAuthenticationAdvise.ShouldBeGood:
            try:
                return await poll_coroutine

            except AirThingsUnauthorizedException as atue:
                _LOGGER.error(
                    AirThingsManager.log(
                        method=poll_coroutine.__name__, 
                        error_code=atue.error_code, 
                        error_details=atue.error_details))

                return None

            except AirThingsException as ate:
                _LOGGER.error(
                    AirThingsManager.log(
                        method=poll_coroutine.__name__, 
                        error_code=ate.error_code, 
                        error_details=ate.error_details))

                return None

        elif advise == AirThingsAuthenticationAdvise.ShouldCheckCredentials:
            _LOGGER.warning(
                AirThingsManager.log(
                    method=poll_coroutine.__name__, 
                    advise=advise, 
                    message='invalid credentials'))

            raise AirThingsInvalidCredentialsException()

        else:
            _LOGGER.warning(
                AirThingsManager.log(
                    method=poll_coroutine.__name__, 
                    advise=advise, 
                    message='cannot execute poll'))

            return None

    def __get_authentication_advise(self) -> AirThingsAuthenticationAdvise:
        if self.tokens is None:
            return AirThingsAuthenticationAdvise.ShouldLogin

        if self.tokens['access_token'] is None:
            return AirThingsAuthenticationAdvise.ShouldLogin
        else:
            if dt.datetime.utcnow() - self.tokens['timestamp'] >= dt.timedelta(seconds=self.tokens['expires_in']):
                if self.tokens['refresh_token'] is None:
                    return AirThingsAuthenticationAdvise.ShouldLogin
                else:
                    return AirThingsAuthenticationAdvise.ShouldRefreshToken
            else:
                return AirThingsAuthenticationAdvise.ShouldBeGood

    async def __assert_ready(self) -> AirThingsAuthenticationAdvise:
        advise = self.__get_authentication_advise()

        if advise == AirThingsAuthenticationAdvise.ShouldLogin:
            return await self.__perform_login()

        elif advise == AirThingsAuthenticationAdvise.ShouldRefreshToken:
            return await self.__perform_refresh()

        return advise

    async def __perform_login(self) -> AirThingsAuthenticationAdvise:
        try:
            token = await AirThingsManager.__get_token(
                session=self.session,
                username=self.username,
                password=self.password)

            consent = await AirThingsManager.__get_consent(
                session=self.session,
                token=token)

            authorization_code = await AirThingsManager.__get_authorization_code(
                session=self.session,
                token=token,
                consent=consent)

            self.tokens = await AirThingsManager.__get_access_and_refresh_token(
                session=self.session,
                authorization_code=authorization_code)

            return AirThingsAuthenticationAdvise.ShouldBeGood

        except AirThingsUnauthorizedException as atue:
            _LOGGER.error(
                AirThingsManager.log(
                    method='__perform_login', 
                    error_code=atue.error_code, 
                    error_details=atue.error_details))

            self.tokens = None
            return AirThingsAuthenticationAdvise.ShouldCheckCredentials

        except AirThingsException as ate:
            _LOGGER.error(
                AirThingsManager.log(
                    method='__perform_login', 
                    error_code=ate.error_code, 
                    error_details=ate.error_details))

            self.tokens = None
            return AirThingsAuthenticationAdvise.ShouldWait

    async def __perform_refresh(self) -> AirThingsAuthenticationAdvise:
        try:
            self.tokens = await AirThingsManager.__refresh_access_and_refresh_token(
                session=self.session,
                previous_refresh_token=self.tokens['refresh_token'])

            return AirThingsAuthenticationAdvise.ShouldBeGood

        except AirThingsUnauthorizedException as atue:
            _LOGGER.error(
                AirThingsManager.log(
                    method='__perform_refresh', 
                    error_code=atue.error_code, 
                    error_details=atue.error_details))

            self.tokens = None
            return AirThingsAuthenticationAdvise.ShouldLogin
            
        except AirThingsException as ate:
            _LOGGER.error(
                AirThingsManager.log(
                    method='__perform_refresh', 
                    error_code=ate.error_code, 
                    error_details=ate.error_details))

            self.tokens = None
            return AirThingsAuthenticationAdvise.ShouldWait


    @staticmethod
    async def __get_token(session: aiohttp.ClientSession, username: str, password: str) -> str:
        async with session.post(
                url=AirThingsManager.format_string(
                    AirThingsConstant.CT_ACCOUNTS_API_BASE,
                    'token'),
                headers={
                    'origin': AirThingsConstant.CT_ACCOUNTS_ORIGIN,
                    'accept': AirThingsConstant.CT_JSON,
                    'content-type': AirThingsConstant.CT_JSON,
                    'user-agent': AirThingsConstant.CT_USER_AGENT,
                },
                json={
                    'username': username,
                    'password': password,
                    'grant_type': 'password',
                    'client_id': 'accounts'
                }) as response:

            if math.floor(response.status / 100) == 2:
                rjson = await response.json()
                return rjson['access_token']

            elif math.floor(response.status / 100) == 4:
                raise AirThingsUnauthorizedException(
                    error_code=response.status,
                    error_details=await response.text())

            else:
                raise AirThingsException(
                    error_code=response.status,
                    error_details=await response.text())

    @staticmethod
    async def __get_consent(session: aiohttp.ClientSession, token: str) -> Optional[Dict[str, Any]]:
        async with session.get(
                url=AirThingsManager.format_string(
                    AirThingsConstant.CT_ACCOUNTS_API_BASE,
                    'consents/dashboard?client_id=dashboard&redirect_uri={0}'.format(
                        AirThingsConstant.CT_DASHBOARD_ORIGIN)),
                headers={
                    'origin': AirThingsConstant.CT_ACCOUNTS_ORIGIN,
                    'accept': AirThingsConstant.CT_JSON,
                    'content-type': AirThingsConstant.CT_JSON,
                    'user-agent': AirThingsConstant.CT_USER_AGENT,
                    'authorization': AirThingsManager.format_string(
                        AirThingsConstant.CT_BEARER_FORMAT,
                        token),
                }) as response:

            if math.floor(response.status / 100) == 2:
                return await response.json()

            elif math.floor(response.status / 100) == 4:
                raise AirThingsUnauthorizedException(
                    error_code=response.status,
                    error_details=await response.text())

            else:
                raise AirThingsException(
                    error_code=response.status,
                    error_details=await response.text())

    @staticmethod
    async def __get_authorization_code(session: aiohttp.ClientSession, token: str, consent) -> str:
        async with session.post(
                url=AirThingsManager.format_string(
                    AirThingsConstant.CT_ACCOUNTS_API_BASE,
                    'authorize?client_id=dashboard&redirect_uri={0}'.format(
                        AirThingsConstant.CT_DASHBOARD_ORIGIN)),
                headers={
                    'origin': AirThingsConstant.CT_ACCOUNTS_ORIGIN,
                    'accept': AirThingsConstant.CT_JSON,
                    'content-type': AirThingsConstant.CT_JSON,
                    'user-agent': AirThingsConstant.CT_USER_AGENT,
                    'authorization': AirThingsManager.format_string(
                        AirThingsConstant.CT_BEARER_FORMAT,
                        token),
                },
                json=consent) as response:

            if math.floor(response.status / 100) == 2:

                rjson = await response.json()
                redirect_uri = rjson['redirect_uri']
                
                fragments = up.urlparse(redirect_uri)
                code = up.parse_qs(fragments.query)['code'][0]

                return code
            
            elif math.floor(response.status / 100) == 4:
                raise AirThingsUnauthorizedException(
                    error_code=response.status,
                    error_details=await response.text())
            else:
                raise AirThingsException(
                    error_code=response.status,
                    error_details=await response.text())

    @staticmethod
    async def __get_access_and_refresh_token(session: aiohttp.ClientSession, authorization_code: str) -> Optional[Dict[str, Any]]:
        async with session.post(
                url=AirThingsManager.format_string(
                    AirThingsConstant.CT_ACCOUNTS_API_BASE,
                    'token'),
                headers={
                    'origin': AirThingsConstant.CT_DASHBOARD_ORIGIN,
                    'accept': AirThingsConstant.CT_JSON,
                    'content-type': AirThingsConstant.CT_JSON,
                    'user-agent': AirThingsConstant.CT_USER_AGENT,
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'cross-site',
                },
                json={
                    'client_id': 'dashboard',
                    'client_secret': AirThingsConstant.CT_DASHBOARD_SECRET,
                    'code': authorization_code,
                    'grant_type': 'authorization_code',
                    'redirect_uri': AirThingsConstant.CT_DASHBOARD_ORIGIN,
                }) as response:

            if math.floor(response.status / 100) == 2:
                
                response_dict = await response.json()

                return {
                    'access_token': response_dict['access_token'], 
                    'refresh_token': response_dict['refresh_token'], 
                    'expires_in': response_dict['expires_in'],
                    'timestamp': dt.datetime.utcnow(),
                }

            elif math.floor(response.status / 100) == 4:
                raise AirThingsUnauthorizedException(
                    error_code=response.status,
                    error_details=await response.text())
            else:
                raise AirThingsException(
                    error_code=response.status,
                    error_details=await response.text())

    @staticmethod
    async def __refresh_access_and_refresh_token(session: aiohttp.ClientSession, previous_refresh_token: str) -> Optional[Dict[str, Any]]:
        async with session.post(
                url=AirThingsManager.format_string(
                    AirThingsConstant.CT_ACCOUNTS_API_BASE,
                    'token'),
                headers={
                    'origin': AirThingsConstant.CT_DASHBOARD_ORIGIN,
                    'accept': AirThingsConstant.CT_JSON,
                    'content-type': AirThingsConstant.CT_JSON,
                    'user-agent': AirThingsConstant.CT_USER_AGENT,
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'cross-site',
                },
                json={
                    'client_id': 'dashboard',
                    'client_secret': AirThingsConstant.CT_DASHBOARD_SECRET,
                    'refresh_token': previous_refresh_token,
                    'grant_type': 'refresh_token',
                }) as response:

            if math.floor(response.status / 100) == 2:
                
                response_dict = await response.json()

                return {
                    'access_token': response_dict['access_token'], 
                    'refresh_token': response_dict['refresh_token'], 
                    'expires_in': response_dict['expires_in'],
                    'timestamp': dt.datetime.utcnow(),
                }

            elif math.floor(response.status / 100) == 4:
                raise AirThingsUnauthorizedException(
                    error_code=response.status,
                    error_details=await response.text())
            else:
                raise AirThingsException(
                    error_code=response.status,
                    error_details=await response.text())

    @staticmethod
    def log(**kwargs):
        logger = ''
        for key, value in kwargs.items():
            logger = logger + '{0}: "{1}" | '.format(key, value)
        return logger        

    @staticmethod
    def format_string(template: AirThingsConstant, *args) -> str:
        return str(template).format(*args)

    @staticmethod
    async def __poll_generic_entity(session: aiohttp.ClientSession, access_token: str, entity: str) -> Optional[Dict[str, Any]]:
        async with session.get(
                url=AirThingsManager.format_string(
                    AirThingsConstant.CT_WEB_API_BASE,
                    entity),
                headers={
                    'origin': AirThingsConstant.CT_DASHBOARD_ORIGIN,
                    'accept': AirThingsConstant.CT_JSON,
                    'content-type': AirThingsConstant.CT_JSON,
                    'user-agent': AirThingsConstant.CT_USER_AGENT,
                    'authorization': access_token,
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'cross-site',
                }) as response:

            if math.floor(response.status / 100) == 2:
                return await response.json()

            elif math.floor(response.status / 100) == 4:
                raise AirThingsUnauthorizedException(
                    error_code=response.status,
                    error_details=await response.text())

            else:
                raise AirThingsException(
                    error_code=response.status,
                    error_details=await response.text())


    @staticmethod
    async def __poll_relay_devices_base(session: aiohttp.ClientSession, access_token: str) -> Optional[Dict[str, Any]]:
        return await AirThingsManager.__poll_generic_entity(
            session=session,
            access_token=access_token,
            entity='relay-devices')

    async def __poll_relay_devices(self) -> Optional[Dict[str, Any]]:
        return await AirThingsManager.__poll_relay_devices_base(
            session=self.session,
            access_token=self.tokens['access_token'])


    @staticmethod
    async def __poll_locations_base(session: aiohttp.ClientSession, access_token: str) -> Optional[Dict[str, Any]]:
        return await AirThingsManager.__poll_generic_entity(
            session=session,
            access_token=access_token,
            entity='location')

    async def __poll_locations(self) -> Optional[Dict[str, Any]]:
        return await AirThingsManager.__poll_locations_base(
            session=self.session,
            access_token=self.tokens['access_token'])


    @staticmethod
    async def __poll_thresholds_base(session: aiohttp.ClientSession, access_token: str) -> Optional[Dict[str, Any]]:
        return await AirThingsManager.__poll_generic_entity(
            session=session,
            access_token=access_token,
            entity='thresholds')

    async def __poll_thresholds(self) -> Optional[Dict[str, Any]]:
        return await AirThingsManager.__poll_thresholds_base(
            session=self.session,
            access_token=self.tokens['access_token'])


    @staticmethod
    async def __poll_me_base(session: aiohttp.ClientSession, access_token: str) -> Optional[Dict[str, Any]]:
        return await AirThingsManager.__poll_generic_entity(
            session=session,
            access_token=access_token,
            entity='me/')

    async def __poll_me(self) -> Optional[Dict[str, Any]]:
        return await AirThingsManager.__poll_me_base(
            session=self.session,
            access_token=self.tokens['access_token'])
