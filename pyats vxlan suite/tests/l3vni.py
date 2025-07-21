import logging
import re
from pyats import aetest
from genie.libs.parser.utils.common import ParserNotFound

logger = logging.getLogger(__name__)

class VxlanL3VniValidation(aetest.Testcase):
    """Validate Layer3 VNI and anycast gateway configuration."""

    @aetest.test
    def test_l3_vni_configuration(self, testbed):
        for name, device in testbed.devices.items():
            with aetest.steps.Step(f"Check L3 VNI configuration on {name}") as step:
                try:
                    try:
                        parsed = device.parse('show nve vni')
                        l3_vnis = [v for v in parsed.get('vni', {}).values() if v.get('type', '').lower() == 'l3']
                        if not l3_vnis:
                            step.skipped("No L3 VNIs configured")
                            continue
                        for vni in l3_vnis:
                            if 'vrf' not in vni:
                                step.failed(f"L3 VNI {vni['vni']} missing VRF association")
                        step.passed(f"{len(l3_vnis)} L3 VNIs configured")
                    except (ParserNotFound, KeyError):
                        output = device.execute('show nve vni')
                        if 'L3' not in output:
                            step.skipped("No L3 VNIs configured")
                        elif re.search(r'L3.*VRF:', output):
                            step.passed("L3 VNIs configured")
                        else:
                            step.failed("L3 VNIs missing VRF association")
                except Exception as exc:
                    step.failed(f"Error: {exc}")

    @aetest.test
    def test_anycast_gateway(self, testbed):
        for name, device in testbed.devices.items():
            with aetest.steps.Step(f"Check anycast gateway on {name}") as step:
                try:
                    output = device.execute('show run | include fabric forwarding anycast-gateway-mac')
                    if not output.strip():
                        step.skipped("No anycast gateway MAC configured")
                        continue
                    svi_output = device.execute('show ip interface brief vlan')
                    if 'vlan' not in svi_output.lower():
                        step.skipped("No SVI interfaces found")
                    else:
                        step.passed("Anycast gateway configured")
                except Exception as exc:
                    step.failed(f"Error: {exc}")
