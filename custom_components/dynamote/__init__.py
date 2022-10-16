from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .websocket import (
	ws_handle_get_dynamote_config_command, 
	ws_handle_set_dynamote_config_command, 
	ws_handle_verify_dynamote_integration_installed,
)

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	async_setup
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
	# register the get_dynamote_config websocket command
	hass.components.websocket_api.async_register_command(ws_handle_get_dynamote_config_command)
	# register the set_dynamote_config websocket command
	hass.components.websocket_api.async_register_command(ws_handle_set_dynamote_config_command)
	# register the verify_dynamote_integration_installed websocket command
	hass.components.websocket_api.async_register_command(ws_handle_verify_dynamote_integration_installed)
	return True
