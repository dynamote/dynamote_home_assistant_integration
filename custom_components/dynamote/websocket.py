from __future__ import annotations

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.components.websocket_api.connection import ActiveConnection
from homeassistant.core import HomeAssistant

from .const import STORAGE_KEY, STORAGE_VERSION

################################################################################################################################
# ws_handle_get_dynamote_config_command
################################################################################################################################


@websocket_api.websocket_command(
    {
        vol.Required("type"): "dynamote/get_dynamote_config",
    }
)
@websocket_api.async_response
async def ws_handle_get_dynamote_config_command(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict
) -> None:
    """Handle get dynamote config command."""
    store = hass.helpers.storage.Store(STORAGE_VERSION, STORAGE_KEY)
    data = await store.async_load()

    if data is None:
        data = {}

    connection.send_result(
        msg["id"],
        {"config": data},
    )


################################################################################################################################
# ws_handle_set_dynamote_config_command
################################################################################################################################


@websocket_api.websocket_command(
    {
        vol.Required("type"): "dynamote/set_dynamote_config",
        vol.Required("config"): object,
    }
)
@websocket_api.async_response
async def ws_handle_set_dynamote_config_command(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict
) -> None:
    """Handle set dynamote config command."""
    store = hass.helpers.storage.Store(STORAGE_VERSION, STORAGE_KEY)
    await store.async_save(msg["config"])

    connection.send_result(
        msg["id"],
        {"data": msg["config"]},
    )


################################################################################################################################
# ws_handle_verify_dynamote_integration_installed
################################################################################################################################


@websocket_api.websocket_command(
    {
        vol.Required("type"): "dynamote/verify_dynamote_integration_installed",
    }
)
@websocket_api.async_response
async def ws_handle_verify_dynamote_integration_installed(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict
) -> None:
    """Handle verify dynamote integration installed command."""
    connection.send_result(
        msg["id"],
        {"result": "success"},
    )
