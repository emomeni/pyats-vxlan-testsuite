import logging
import re
from pyats import aetest
from genie.libs.parser.utils.common import ParserNotFound

logger = logging.getLogger(__name__)

class CommonSetup(aetest.CommonSetup):
    """Connect to all devices and verify NX-OS version."""

    @aetest.subsection
    def connect_to_devices(self, testbed):
        for name, device in testbed.devices.items():
            logger.info(f"Connecting to {name}")
            try:
                device.connect()
                logger.info(f"Connected to {name}")
            except Exception as exc:
                self.failed(f"Failed to connect to {name}: {exc}")

    @aetest.subsection
    def check_nxos_version(self, testbed):
        for name, device in testbed.devices.items():
            try:
                try:
                    parsed = device.parse('show version')
                    version = float(parsed['platform']['software']['system_version'])
                except (ParserNotFound, KeyError):
                    output = device.execute('show version')
                    match = re.search(r'system:\s+version\s+(\d+\.\d+)', output)
                    version = float(match.group(1)) if match else 0
                if version < 7.0:
                    self.failed(f"{name} running NX-OS {version}, VXLAN requires 7.0+")
                logger.info(f"{name} NX-OS version {version}")
            except Exception as exc:
                logger.warning(f"Could not verify NX-OS version on {name}: {exc}")

class CommonCleanup(aetest.CommonCleanup):
    """Disconnect from all devices."""

    @aetest.subsection
    def disconnect_devices(self, testbed):
        for name, device in testbed.devices.items():
            logger.info(f"Disconnecting from {name}")
            device.disconnect()
