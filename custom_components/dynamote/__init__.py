from __future__ import annotations

from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.components import websocket_api
from aiohttp import ClientTimeout
from .const import DOMAIN, STORAGE_VERSION, STORAGE_KEY

import voluptuous as vol
import socket

import logging
_LOGGER = logging.getLogger(__name__)

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	ws_handle_get_dynamote_config_command
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
@websocket_api.websocket_command(
	{
		vol.Required("type"): "dynamote/get_dynamote_config",
	}
)
@websocket_api.async_response
async def ws_handle_get_dynamote_config_command(hass: HomeAssistant, connection: ActiveConnection, msg: dict) -> None:

	store = hass.helpers.storage.Store(STORAGE_VERSION, STORAGE_KEY)
	data = await store.async_load()

	if (data is None):
		data = {}

	connection.send_result(
		msg["id"],
		{
			"config": data
		},
	)

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	ws_handle_set_dynamote_config_command
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
@websocket_api.websocket_command(
	{
		vol.Required("type"): "dynamote/set_dynamote_config",
		vol.Required("config"): object,
	}
)
@websocket_api.async_response
async def ws_handle_set_dynamote_config_command(hass: HomeAssistant, connection: ActiveConnection, msg: dict) -> None:

	store = hass.helpers.storage.Store(STORAGE_VERSION, STORAGE_KEY)
	await store.async_save(msg["config"])

	connection.send_result(
		msg["id"],
		{
			"data": msg["config"]
		},
	)

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	handle_send_command_service
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
@callback
async def handle_send_command_service(call: ServiceCall) -> None:

  # TODO
	# if resolve error, educate about MDNS setup in hass (do this in the README)
	# mdns often fails, do it another way, or test it outside container?

	#
	# Verify that the required parameters are present in the service call
	#

	if "commandId" in call.data:
		targetCommandId = call.data["commandId"]
	else:
		_LOGGER.error("Dynamote send_command service error, commandId was not provided in the service call")
		return

	if "deviceName" in call.data and "ipAddress" in call.data:
		_LOGGER.error("Dynamote send_command service error, only one of deviceName and ipAddress can be specified in the service call")
		return

	#
	# Allow the user to override the deviceName or IpAddress
	#
	
	if "deviceName" in call.data:
		deviceName = call.data["deviceName"]

	if "ipAddress" in call.data:
		ipAddress = call.data["ipAddress"]

	#
	# Verify that the required parameters are present in saved config
	#

	global hassObj
	store = hassObj.helpers.storage.Store(STORAGE_VERSION, STORAGE_KEY)
	configData = await store.async_load()

	for configEntry in configData:
		if "commandId" in configEntry and configEntry["commandId"] == targetCommandId:
			commandConfig = configEntry
	if not 'commandConfig' in locals():
		_LOGGER.error("Dynamote send_command service error, could not find the commandId \"" + targetCommandId + "\" in the saved config")
		return

	if not 'deviceName' in locals() and not "ipAddress" in locals() and "deviceName" in commandConfig:
		deviceName = commandConfig["deviceName"]

	if not 'ipAddress' in locals() and not "deviceName" in locals() and "ipAddress" in commandConfig:
		ipAddress = commandConfig["ipAddress"]

	if not'deviceName' in locals() and not "ipAddress" in locals():
		_LOGGER.error("Dynamote send_command service error, the deviceName or ipAddress was not provided in the saved config or service call")
		return

	if not "cmdBytesString" in commandConfig:
		_LOGGER.error("Dynamote send_command service error, the cmdBytesString was not provided in the saved config")
		return
	cmdBytesString = commandConfig["cmdBytesString"]

	#
	# convert the cmdBytesString string to binary hex data
	#

	# for example, cmdBytesString = "[18, 8, 10, 4, 116, 101, 115, 116, 18, 0]"
	byteStrings = list(map(int, cmdBytesString.replace('[', '').replace(']', '').split(', ')))
	hexdata = ''.join([chr(item) for item in byteStrings])

	#
	# get the ip address for the device on the local network with the given hostname
	#

	if not 'ipAddress' in locals():
		try:
			ipAddress = socket.gethostbyname(deviceName + '.local')
		except:
			_LOGGER.error("Dynamote send_command service error, could not find device with hostname " + deviceName + ".local on the local network")
			return

	#
	# post to the device
	#

	try:
		url = 'http://' + ipAddress + '/dynamoteCmd'
		session = async_get_clientsession(hassObj)
		await session.post(url, data=hexdata, timeout=ClientTimeout(total=5))
	except:
		_LOGGER.error("Dynamote send_command service error, failed to send command to device")
		return

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	async_setup
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
	# resister the Dynamote service
	hass.services.async_register(DOMAIN, "send_command", handle_send_command_service)
	# register the get_dynamote_config websocket command
	hass.components.websocket_api.async_register_command(ws_handle_get_dynamote_config_command)
	# register the set_dynamote_config websocket command
	hass.components.websocket_api.async_register_command(ws_handle_set_dynamote_config_command)
	
	global hassObj
	hassObj = hass

	return True
