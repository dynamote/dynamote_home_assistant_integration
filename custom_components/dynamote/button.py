"""Support for Dynamote buttons."""

from asyncio import run_coroutine_threadsafe
from collections.abc import Callable
import logging

import voluptuous as vol

from homeassistant.components.button import PLATFORM_SCHEMA, ButtonEntity
from homeassistant.components.mqtt import async_publish
from homeassistant.const import CONF_COMMAND
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import STORAGE_KEY, STORAGE_VERSION

_LOGGER = logging.getLogger(__name__)


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_COMMAND): cv.string,
    }
)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        [DynamoteSwitch(config[CONF_COMMAND], hass)], update_before_add=False
    )


class DynamoteSwitch(ButtonEntity):
    """Dynamote Switch class."""

    def __init__(self, commandId: str, hass: HomeAssistant) -> None:
        """Initialize the Dynamote Switch."""
        super().__init__()
        self._commandId = commandId
        self.hass = hass

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._commandId

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the button."""
        return self._commandId

    def press(self) -> None:
        """Run async_press synchronously."""
        run_coroutine_threadsafe(self.async_press(), self.hass.loop)

    async def async_press(self) -> None:
        """Send the command to the IR device."""
        try:
            commandConfig = await self._getConfigForCommand()
        except ValueError as e:
            _LOGGER.error(e)
            return

        # get the topic
        try:
            if commandConfig["cmd"]["useCustomCmd"] is True:
                topic = commandConfig["cmd"]["customCmdTopic"]
            else:
                topic = f"cmnd/{commandConfig['topic']}/irsend"
        except Exception as e:
            raise ValueError(
                "Error, attempted to send a command with Dynamote, for a command that does exist but is not configured properly"
            ) from e

        # get the cmd to send (payload)
        try:
            if commandConfig["cmd"]["useCustomCmd"] is True:
                cmdPayload = commandConfig["cmd"]["customCmdPayload"]
            else:
                cmdPayload = commandConfig["cmd"]["irCmd"]
        except Exception as e:
            raise ValueError(
                "Error, attempted to send a command with Dynamote, for a command that does exist but is not configured properly"
            ) from e

        # send over MQTT
        await async_publish(
            self.hass,
            topic,
            cmdPayload,
            2,
        )

    async def _getConfigForCommand(self) -> str:
        # get the saved command configs
        store = self.hass.helpers.storage.Store(STORAGE_VERSION, STORAGE_KEY)
        configData = await store.async_load()

        # verify that there is a proper config saved for this command ID
        for configEntry in configData:
            if (
                "commandId" in configEntry
                and configEntry["commandId"] == self._commandId
            ):
                commandConfig = configEntry

        if "commandConfig" not in locals():
            raise ValueError(
                "Error, attempted to send a command with Dynamote, for a command that does not exist"
            )

        if "cmd" not in commandConfig or "topic" not in commandConfig:
            raise ValueError(
                "Error, attempted to send a command with Dynamote, for a command that does exist but is not configured properly"
            )

        return commandConfig
