
from typing import Callable, Optional

from homeassistant.components.mqtt import async_publish
from homeassistant.components.button import ButtonEntity
from homeassistant.components.button import PLATFORM_SCHEMA
from homeassistant.const import CONF_COMMAND, CONF_NAME
from .const import STORAGE_VERSION, STORAGE_KEY
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType, HomeAssistantType
from asyncio import run_coroutine_threadsafe

import voluptuous as vol
import homeassistant.helpers.config_validation as cv
import json
import logging
_LOGGER = logging.getLogger(__name__)


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_COMMAND): cv.string,
        vol.Required(CONF_NAME): cv.string,
    }
)


async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
	"""Set up the sensor platform."""
	async_add_entities([DynamoteSwitch(config[CONF_COMMAND], config[CONF_NAME], hass)], update_before_add=False)


class DynamoteSwitch(ButtonEntity):
	""" Dynamote Switch class """

	def __init__(self, name: str, commandId: str, hass: HomeAssistantType):
		super().__init__()
		self._commandId = commandId
		self._name = name
		self.hass = hass

	@property
	def name(self) -> str:
			"""Return the name of the entity."""
			return self._name

	@property
	def unique_id(self) -> str:
			"""Return the unique ID of the button."""
			return self._name

	def press(self) -> None:
		# run async_press synchronously
		run_coroutine_threadsafe(
        self.async_press(), self.hass.loop
    )

	async def async_press(self) -> None:
		try:
			commandConfig = await self._getConfigForCommand()
		except ValueError as e:
			_LOGGER.error(e)
			return;

		# get the topic
		try:
			if commandConfig['cmd']['useCustomCmd'] == True:
				topic = commandConfig['cmd']['customCmdTopic']
			else:
				topic = f"cmnd/${commandConfig['topic']}/irsend"
		except e:
			raise ValueError("Error, attempted to send a command with Dynamote, for a command that does exist but is not configured properly")

		# get the cmd to send (payload)
		try:
			if commandConfig['cmd']['useCustomCmd'] == True:
				cmdPayload = commandConfig['cmd']['customCmdPayload']
			else:
				cmdPayload = commandConfig['cmd']['irCmd']
		except e:
			raise ValueError("Error, attempted to send a command with Dynamote, for a command that does exist but is not configured properly")

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
			if "commandId" in configEntry and configEntry["commandId"] == self._commandId:
				commandConfig = configEntry

		if not 'commandConfig' in locals():
			raise ValueError("Error, attempted to send a command with Dynamote, for a command that does not exist")

		if not "cmd" in commandConfig or not "topic" in commandConfig:
			raise ValueError("Error, attempted to send a command with Dynamote, for a command that does exist but is not configured properly")

		return commandConfig