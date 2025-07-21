import logging
import re
from pyats import aetest
from genie.libs.parser.utils.common import ParserNotFound

logger = logging.getLogger(__name__)

class VxlanMacAddressValidation(aetest.Testcase):
    """Validate MAC address learning in VXLAN VLANs."""

    @aetest.test
    def test_mac_address_table(self, testbed):
        for name, device in testbed.devices.items():
            with aetest.steps.Step(f"Check MAC learning on {name}") as step:
                try:
                    vni_output = device.execute('show nve vni')
                    vlans = re.findall(r'VLAN:\s*(\d+)', vni_output)
                    if not vlans:
                        step.skipped("No VXLAN VLANs found")
                        continue
                    mac_learned = False
                    for vlan in vlans[:3]:
                        try:
                            parsed = device.parse(f'show mac address-table vlan {vlan}')
                            if parsed.get('mac_table'):  # if dictionary not empty
                                mac_learned = True
                                break
                        except ParserNotFound:
                            output = device.execute(f'show mac address-table vlan {vlan}')
                            if re.search(r'[0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4}', output.lower()):
                                mac_learned = True
                                break
                    if mac_learned:
                        step.passed("MAC addresses learned")
                    else:
                        step.failed("No MAC addresses learned")
                except Exception as exc:
                    step.failed(f"Error: {exc}")
