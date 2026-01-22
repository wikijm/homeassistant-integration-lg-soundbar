"""Support for LG Soundbar media player."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import temescal
from .const import (
    CONF_PORT,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DOMAIN,
    MANUFACTURER,
    MODEL,
    SCAN_INTERVAL_SECONDS,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the LG Soundbar media player platform."""
    host = entry.data[CONF_HOST]
    port = entry.data.get(CONF_PORT, DEFAULT_PORT)
    name = entry.data.get(CONF_NAME, DEFAULT_NAME)

    _LOGGER.debug("Setting up LG Soundbar at %s:%s", host, port)

    device = LGSoundbarMediaPlayer(name, host, port, entry.entry_id, hass)
    async_add_entities([device], True)


class LGSoundbarMediaPlayer(MediaPlayerEntity):
    """Representation of an LG Soundbar."""

    def __init__(self, name: str, host: str, port: int, entry_id: str, hass: HomeAssistant) -> None:
        """Initialize the LG Soundbar device."""
        self._attr_name = name
        self._host = host
        self._port = port
        self._attr_unique_id = f"{host}_{port}"
        self._entry_id = entry_id
        self._hass = hass
        
        # State attributes
        self._attr_state = MediaPlayerState.ON
        self._volume = 0
        self._volume_min = 0
        self._volume_max = 100
        self._attr_is_volume_muted = False
        self._function = -1
        self._functions = []
        self._equaliser = -1
        self._equalisers = []
        self._bass = 0
        self._treble = 0
        self._rear_volume = 0
        self._woofer_volume = 0
        
        # Create temescal device
        self._device = temescal.Temescal(
            host,
            port=port,
            callback=self._handle_event,
            loop=hass.loop
        )
        
        # Supported features
        self._attr_supported_features = (
            MediaPlayerEntityFeature.VOLUME_SET
            | MediaPlayerEntityFeature.VOLUME_MUTE
            | MediaPlayerEntityFeature.VOLUME_STEP
            | MediaPlayerEntityFeature.SELECT_SOURCE
            | MediaPlayerEntityFeature.SELECT_SOUND_MODE
        )

    def _handle_event(self, response: dict[str, Any]) -> None:
        """Handle responses from the soundbar."""
        data = response.get("data", {})
        msg = response.get("msg", "")
        
        if msg == "EQ_VIEW_INFO":
            if "i_bass" in data:
                self._bass = data["i_bass"]
            if "i_treble" in data:
                self._treble = data["i_treble"]
            if "ai_eq_list" in data:
                self._equalisers = data["ai_eq_list"]
            if "i_curr_eq" in data:
                self._equaliser = data["i_curr_eq"]
                
        elif msg == "SPK_LIST_VIEW_INFO":
            if "i_vol" in data:
                self._volume = data["i_vol"]
            if "i_vol_min" in data:
                self._volume_min = data["i_vol_min"]
            if "i_vol_max" in data:
                self._volume_max = data["i_vol_max"]
            if "b_mute" in data:
                self._attr_is_volume_muted = data["b_mute"]
            if "i_curr_func" in data:
                self._function = data["i_curr_func"]
                
        elif msg == "FUNC_VIEW_INFO":
            if "i_curr_func" in data:
                self._function = data["i_curr_func"]
            if "ai_func_list" in data:
                self._functions = data["ai_func_list"]
                
        elif msg == "SETTING_VIEW_INFO":
            if "i_rear_level" in data:
                self._rear_volume = data["i_rear_level"]
            if "i_woofer_level" in data:
                self._woofer_volume = data["i_woofer_level"]
            if "i_curr_eq" in data:
                self._equaliser = data["i_curr_eq"]
        
        # Schedule update
        self.schedule_update_ha_state()

    @property
    def device_info(self):
        """Return device information about this LG Soundbar."""
        return {
            "identifiers": {(DOMAIN, self._attr_unique_id)},
            "name": self._attr_name,
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }

    @property
    def volume_level(self) -> float | None:
        """Volume level of the media player (0..1)."""
        if self._volume_max != 0:
            return self._volume / self._volume_max
        return 0.0

    @property
    def sound_mode(self) -> str | None:
        """Return the current sound mode."""
        if self._equaliser == -1 or self._equaliser >= len(temescal.equalisers):
            return None
        return temescal.equalisers[self._equaliser]

    @property
    def sound_mode_list(self) -> list[str] | None:
        """Return the available sound modes."""
        if not self._equalisers:
            return None
        modes = []
        for equaliser in self._equalisers:
            if equaliser < len(temescal.equalisers):
                modes.append(temescal.equalisers[equaliser])
        return sorted(modes) if modes else None

    @property
    def source(self) -> str | None:
        """Return the current input source."""
        if self._function == -1 or self._function >= len(temescal.functions):
            return None
        return temescal.functions[self._function]

    @property
    def source_list(self) -> list[str] | None:
        """List of available input sources."""
        if not self._functions:
            return None
        sources = []
        for function in self._functions:
            if function < len(temescal.functions):
                sources.append(temescal.functions[function])
        return sorted(sources) if sources else None

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()
        await self._device.connect()

    async def async_will_remove_from_hass(self) -> None:
        """Run when entity will be removed from hass."""
        await super().async_will_remove_from_hass()
        await self._device.disconnect()

    async def async_update(self) -> None:
        """Update the state of the device."""
        _LOGGER.debug("Updating LG Soundbar state from %s:%s", self._host, self._port)
        await self._device.get_eq()
        await self._device.get_info()
        await self._device.get_func()
        await self._device.get_settings()
        await self._device.get_product_info()

    async def async_set_volume_level(self, volume: float) -> None:
        """Set volume level, range 0..1."""
        volume_int = int(volume * self._volume_max)
        await self._device.set_volume(volume_int)

    async def async_volume_up(self) -> None:
        """Volume up the soundbar."""
        new_volume = min(self._volume_max, self._volume + 1)
        await self._device.set_volume(new_volume)

    async def async_volume_down(self) -> None:
        """Volume down the soundbar."""
        new_volume = max(self._volume_min, self._volume - 1)
        await self._device.set_volume(new_volume)

    async def async_mute_volume(self, mute: bool) -> None:
        """Mute (true) or unmute (false) the soundbar."""
        await self._device.set_mute(mute)

    async def async_select_source(self, source: str) -> None:
        """Select input source."""
        try:
            source_index = temescal.functions.index(source)
            await self._device.set_func(source_index)
        except ValueError:
            _LOGGER.error("Invalid source: %s", source)

    async def async_select_sound_mode(self, sound_mode: str) -> None:
        """Set Sound Mode for soundbar."""
        try:
            eq_index = temescal.equalisers.index(sound_mode)
            await self._device.set_eq(eq_index)
        except ValueError:
            _LOGGER.error("Invalid sound mode: %s", sound_mode)
