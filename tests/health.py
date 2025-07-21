import logging
import re
from pyats import aetest

logger = logging.getLogger(__name__)

MAX_VNIS = 16000
WARN_VNIS = 8000
CRIT_VNIS = 12000

class VxlanHealthCheck(aetest.Testcase):
    """Overall VXLAN health and resource checks."""

    @aetest.test
    def test_vxlan_statistics(self, testbed):
        for name, device in testbed.devices.items():
            with aetest.steps.Step(f"Check NVE counters on {name}") as step:
                try:
                    output = device.execute('show interface nve1 counters detailed')
                    errors = []
                    for line in output.split('\n'):
                        if any(k in line.lower() for k in ['error', 'drop', 'discard', 'invalid']):
                            numbers = re.findall(r'\d+', line)
                            if any(int(num) > 0 for num in numbers):
                                errors.append(line.strip())
                    if errors:
                        step.failed(f"Errors found: {errors}")
                    else:
                        step.passed("No interface errors")
                except Exception as exc:
                    step.failed(f"Error: {exc}")

    @aetest.test
    def test_vxlan_resource_usage(self, testbed):
        for name, device in testbed.devices.items():
            with aetest.steps.Step(f"Check VNI usage on {name}") as step:
                try:
                    output = device.execute('show nve vni')
                    vni_count = len([l for l in output.split('\n') if re.match(r'^\s*\d+', l)])
                    if vni_count > CRIT_VNIS:
                        step.failed(f"High VNI usage: {vni_count}")
                    elif vni_count > WARN_VNIS:
                        step.passed(f"Moderate VNI usage: {vni_count}")
                    else:
                        step.passed(f"Normal VNI usage: {vni_count}")
                except Exception as exc:
                    step.failed(f"Error: {exc}")
