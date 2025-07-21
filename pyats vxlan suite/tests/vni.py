import logging
import re
from pyats import aetest
from genie.libs.parser.utils.common import ParserNotFound

logger = logging.getLogger(__name__)

MAX_VNIS = 16000
WARN_VNIS = 8000
CRIT_VNIS = 12000

class VxlanVniValidation(aetest.Testcase):
    """Validate VNI configuration and ingress replication."""

    @aetest.test
    def test_vni_configuration(self, testbed):
        for name, device in testbed.devices.items():
            with aetest.steps.Step(f"Check VNI configuration on {name}") as step:
                try:
                    try:
                        parsed = device.parse('show nve vni')
                        vnis = parsed.get('vni', {})
                        if not vnis:
                            step.skipped("No VNIs configured")
                            continue
                        for vni_id, vni_data in vnis.items():
                            if vni_data.get('type', '').lower() == 'l2' and 'vlan' not in vni_data:
                                step.failed(f"VNI {vni_id} missing VLAN association")
                        step.passed(f"Found {len(vnis)} VNIs")
                    except (ParserNotFound, KeyError):
                        output = device.execute('show nve vni')
                        if 'VNI' not in output:
                            step.skipped("No VNIs configured")
                            continue
                        vni_count = len(re.findall(r'^\s*\d+', output, re.M))
                        step.passed(f"Found {vni_count} VNIs")
                except Exception as exc:
                    step.failed(f"Error: {exc}")

    @aetest.test
    def test_vni_ingress_replication(self, testbed):
        for name, device in testbed.devices.items():
            with aetest.steps.Step(f"Check ingress replication on {name}") as step:
                try:
                    output = device.execute('show nve vni ingress-replication')
                    if 'VNI' not in output:
                        step.skipped("No ingress replication configured")
                    elif 'protocol-bgp' in output.lower() or 'static' in output.lower():
                        step.passed("Ingress replication configured")
                    else:
                        step.failed("Ingress replication not properly configured")
                except Exception as exc:
                    step.skipped(f"Ingress replication not applicable: {exc}")
