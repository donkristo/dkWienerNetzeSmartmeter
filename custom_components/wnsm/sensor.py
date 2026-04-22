"""
WienerNetze Smartmeter sensor platform
"""
import collections.abc
import logging
from datetime import timedelta
from typing import Optional

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import core, config_entries
from homeassistant.components.sensor import (
    PLATFORM_SCHEMA
)
from homeassistant.const import (
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_DEVICE_ID
)
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
)
from .api import Smartmeter
from .const import ATTRS_ZAEHLPUNKTE_CALL, CONF_ZAEHLPUNKTE, DOMAIN
from .utils import translate_dict
from .wnsm_sensor import WNSMSensor

_LOGGER = logging.getLogger(__name__)

# Time between updating data from Wiener Netze
SCAN_INTERVAL = timedelta(minutes=60 * 6)
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required(CONF_DEVICE_ID): cv.string,
    }
)


async def _async_get_active_zaehlpunkte(hass: core.HomeAssistant, config: dict) -> list[dict]:
    smartmeter = Smartmeter(config[CONF_USERNAME], config[CONF_PASSWORD])
    await hass.async_add_executor_job(smartmeter.login)
    contracts = await hass.async_add_executor_job(smartmeter.zaehlpunkte)

    zaehlpunkte = []
    if contracts is not None and isinstance(contracts, list):
        for contract in contracts:
            customer_id = contract.get("geschaeftspartner")
            for zaehlpunkt in contract.get("zaehlpunkte", []):
                if zaehlpunkt.get("isActive"):
                    zaehlpunkte.append(
                        translate_dict(
                            {**zaehlpunkt, "geschaeftspartner": customer_id},
                            ATTRS_ZAEHLPUNKTE_CALL,
                        )
                    )
    return zaehlpunkte


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Setup sensors from a config entry created in the integrations UI."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    try:
        zaehlpunkte = await _async_get_active_zaehlpunkte(hass, config)
        _LOGGER.info(
            "WienerNetze setup found %s active zaehlpunkte: %s",
            len(zaehlpunkte),
            [zp["zaehlpunktnummer"] for zp in zaehlpunkte],
        )
    except Exception as exception:  # pylint: disable=broad-except
        _LOGGER.warning(
            "Could not refresh WienerNetze zaehlpunkte during setup, using stored config: %s",
            exception,
        )
        zaehlpunkte = config[CONF_ZAEHLPUNKTE]

    if not zaehlpunkte:
        _LOGGER.warning("No active WienerNetze zaehlpunkte found during setup")
        return

    wnsm_sensors = [
        WNSMSensor(config[CONF_USERNAME], config[CONF_PASSWORD], zp["zaehlpunktnummer"])
        for zp in zaehlpunkte
    ]
    async_add_entities(wnsm_sensors, update_before_add=True)


async def async_setup_platform(
    hass: core.HomeAssistant,  # pylint: disable=unused-argument
    config: ConfigType,
    async_add_entities: collections.abc.Callable,
    discovery_info: Optional[
        DiscoveryInfoType
    ] = None,  # pylint: disable=unused-argument
) -> None:
    """Set up the sensor platform by adding it into configuration.yaml"""
    wnsm_sensor = WNSMSensor(config[CONF_USERNAME], config[CONF_PASSWORD], config[CONF_DEVICE_ID])
    async_add_entities([wnsm_sensor], update_before_add=True)
