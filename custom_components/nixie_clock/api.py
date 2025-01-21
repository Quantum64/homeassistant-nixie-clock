"""Sample API Client."""

from __future__ import annotations

import socket
from typing import Any
from urllib.parse import urlencode

import aiohttp
import async_timeout

from custom_components.nixie_clock.const import PARAM_BRIGHTNESS

API_BASE = "https://api.daliborfarny.com"

class NixieApiClientError(Exception):
    """Exception to indicate a general API error."""


class NixieApiClientCommunicationError(
    NixieApiClientError,
):
    """Exception to indicate a communication error."""


class NixieApiClientAuthenticationError(
    NixieApiClientError,
):
    """Exception to indicate an authentication error."""


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    if response.status in (401, 403):
        msg = "Invalid credentials"
        raise NixieApiClientAuthenticationError(
            msg,
        )
    response.raise_for_status()


class NixieApiClient:
    def __init__(
        self,
        device_id: str,
        username: str,
        password: str,
        session: aiohttp.ClientSession,
    ) -> None:
        self._device_id = device_id
        self._username = username
        self._password = password
        self._session = session
        self._access_token = None

    async def async_get_data(self) -> dict:
        data = {}
        for device in (await self._api_wrapper(
                method="GET",
                endpoint=f"devices",
        ))["data"]:
            if device["id"] == self._device_id:
                data["name"] = device["name"]
                break
            else:
                raise NixieApiClientError(f"Device {self._device_id} not found")
        parameters = [PARAM_BRIGHTNESS]
        for parameter in parameters:
            data[parameter] = (await self._api_wrapper(
                method="GET",
                endpoint=f"devices/{self._device_id}/{parameter}",
            ))["data"]["value"]
        return data


    async def async_set_param(self, param: str, value: Any) -> Any:
        return await self._api_wrapper(
            method="POST",
            endpoint=f"devices/{self._device_id}/{param}",
            data={"arg": str(value)},
            headers={"Content-type": "application/x-www-form-urlencoded"},
        )

    async def _api_wrapper(
        self,
        method: str,
        endpoint: str,
        data: dict | None = None,
        params: dict | None = None,
        headers: dict | None = None,
    ) -> dict:
        if self._access_token is None:
            try:
                async with async_timeout.timeout(10):
                    response = await self._session.request(
                        method="POST",
                        url=f"{API_BASE}/oauth/token",
                        data={
                            "client_id": "3rdparty",
                            "grant_type": "password",
                            "username": self._username,
                            "password": self._password,
                            "client_secret": "ws7TQHXp5W6444t4",
                        },
                        headers={"Content-type": "multipart/form-data"},
                    )
                    _verify_response_or_raise(response)
                    data = await response.json()
                    self._access_token = data["data"]["access_token"]
            except TimeoutError as exception:
                msg = f"Timeout error fetching information - {exception}"
                raise NixieApiClientCommunicationError(
                    msg,
                ) from exception
            except (aiohttp.ClientError, socket.gaierror) as exception:
                msg = f"Error fetching information - {exception}"
                raise NixieApiClientCommunicationError(
                    msg,
                ) from exception
            except Exception as exception:  # pylint: disable=broad-except
                msg = f"Something really wrong happened! - {exception}"
                raise NixieApiClientError(
                    msg,
                ) from exception
        params = params or {}
        if token := self._access_token:
            if method == "GET":
                params["client_id"] = "3rdparty"
                params["client_secret"] = "ws7TQHXp5W6444t4"
                params["access_token"] = token
            elif method == "POST":
                data["client_id"] = "3rdparty"
                data["client_secret"] = "ws7TQHXp5W6444t4"
                data["access_token"] = token
        endpoint = f"{API_BASE}/v1/{endpoint}?{urlencode(params)}"
        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=endpoint,
                    headers=headers,
                    json=data,
                )
                _verify_response_or_raise(response)
                return await response.json()

        except TimeoutError as exception:
            msg = f"Timeout error fetching information - {exception}"
            raise NixieApiClientCommunicationError(
                msg,
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            raise NixieApiClientCommunicationError(
                msg,
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Something really wrong happened! - {exception}"
            raise NixieApiClientError(
                msg,
            ) from exception
