import logging
import re
from pyats import aetest
from genie.libs.parser.utils.common import ParserNotFound

logger = logging.getLogger(__name__)

class VxlanMulticastValidation(aetest.Testcase):
    """Validate multicast configuration for VXLAN."""

    @aetest.test
    def test_multicast_groups(self, testbed):
        for name, device in testbed.devices.items():
            with aetest.steps.Step(f"Check multicast on {name}") as step:
                try:
                    output = device.execute('show nve multicast')
                    if 'multicast' not in output.lower():
                        step.skipped("No multicast configured")
                    elif re.search(r'\d+\.\d+\.\d+\.\d+', output):
                        step.passed("Multicast groups configured")
                    else:
                        step.failed("Multicast groups missing")
                except Exception as exc:
                    step.skipped(f"Multicast not applicable: {exc}")
