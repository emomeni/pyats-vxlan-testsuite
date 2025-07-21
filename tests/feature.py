import logging
from pyats import aetest
from genie.libs.parser.utils.common import ParserNotFound

logger = logging.getLogger(__name__)

class VxlanFeatureValidation(aetest.Testcase):
    """Verify VXLAN and NVE features are enabled."""

    @aetest.test
    def test_vxlan_feature_enabled(self, testbed):
        for name, device in testbed.devices.items():
            with aetest.steps.Step(f"Check VXLAN feature on {name}") as step:
                try:
                    try:
                        parsed = device.parse('show feature')
                        if not parsed['feature']['vn-segment-vlan-based']['enabled']:
                            step.failed("VXLAN feature not enabled")
                        else:
                            step.passed("Feature enabled")
                    except (ParserNotFound, KeyError):
                        output = device.execute('show feature | include vn-segment')
                        if 'enabled' in output.lower():
                            step.passed("Feature enabled")
                        else:
                            step.failed("VXLAN feature not enabled")
                except Exception as exc:
                    step.failed(f"Error: {exc}")

    @aetest.test
    def test_nve_feature_enabled(self, testbed):
        for name, device in testbed.devices.items():
            with aetest.steps.Step(f"Check NVE feature on {name}") as step:
                try:
                    try:
                        parsed = device.parse('show feature')
                        if not parsed['feature']['nv overlay']['enabled']:
                            step.failed("NVE feature not enabled")
                        else:
                            step.passed("Feature enabled")
                    except (ParserNotFound, KeyError):
                        output = device.execute('show feature | include nv overlay')
                        if 'enabled' in output.lower():
                            step.passed("Feature enabled")
                        else:
                            step.failed("NVE feature not enabled")
                except Exception as exc:
                    step.failed(f"Error: {exc}")
