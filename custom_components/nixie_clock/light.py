"""Switch platform for integration_blueprint."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any

from homeassistant.components.light import LightEntity, LightEntityDescription, ATTR_BRIGHTNESS
from homeassistant.util.percentage import percentage_to_ranged_value

from .const import PARAM_BRIGHTNESS
from .entity import NixieEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import NixieUpdateCoordinator
    from .data import NixieConfigEntry

ENTITY_DESCRIPTIONS = (
    LightEntityDescription(
        key="nixie_clock",
        name="Nixie Clock Display",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: NixieConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities(
        NixieDisplay(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class NixieDisplay(NixieEntity, LightEntity):
    def __init__(
        self,
        coordinator: NixieUpdateCoordinator,
        entity_description: LightEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_supported_color_modes = {"brightness"}
        self._attr_color_mode = "brightness"

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.get(PARAM_BRIGHTNESS) > 1

    @property
    def brightness(self) -> int | None:
        brightness = self.coordinator.data.get(PARAM_BRIGHTNESS)
        if brightness is not None:
            brightness = int(brightness)
        if brightness == 1:
            return 0
        return brightness

    async def change_brightness(self, brightness: int) -> None:
        await self.coordinator.config_entry.runtime_data.client.async_set_param(PARAM_BRIGHTNESS, brightness)
        await self.coordinator.async_request_refresh()


    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.config_entry.runtime_data.client.async_set_param(PARAM_BRIGHTNESS, math.ceil(percentage_to_ranged_value((1, 255), kwargs.get(ATTR_BRIGHTNESS, 255))))
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **_: Any) -> None:
        await self.coordinator.config_entry.runtime_data.client.async_set_param(PARAM_BRIGHTNESS, 1)
        await self.coordinator.async_request_refresh()


