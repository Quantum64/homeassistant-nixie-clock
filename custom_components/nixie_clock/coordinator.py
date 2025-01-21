"""DataUpdateCoordinator for integration_blueprint."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    NixieApiClientAuthenticationError,
    NixieApiClientError,
)

if TYPE_CHECKING:
    from .data import NixieConfigEntry


class NixieUpdateCoordinator(DataUpdateCoordinator):
    config_entry: NixieConfigEntry

    async def _async_update_data(self) -> Any:
        try:
            return await self.config_entry.runtime_data.client.async_get_data()
        except NixieApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except NixieApiClientError as exception:
            raise UpdateFailed(exception) from exception
