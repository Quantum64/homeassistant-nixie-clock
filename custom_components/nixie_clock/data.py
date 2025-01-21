"""Custom types for integration_blueprint."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import NixieApiClient
    from .coordinator import NixieUpdateCoordinator


type NixieConfigEntry = ConfigEntry[NixieData]


@dataclass
class NixieData:
    client: NixieApiClient
    coordinator: NixieUpdateCoordinator
    integration: Integration
