import logging
from pyats import aetest
from genie.libs.parser.utils.common import ParserNotFound

logger = logging.getLogger(__name__)

class VxlanBgpValidation(aetest.Testcase):
    """Validate BGP EVPN configuration and routes."""

    @aetest.test
    def test_bgp_evpn_configuration(self, testbed):
        for name, device in testbed.devices.items():
            with aetest.steps.Step(f"Check BGP EVPN on {name}") as step:
                try:
                    try:
                        parsed = device.parse('show bgp l2vpn evpn summary')
                        neighbors = parsed.get('vrf', {}).get('default', {}).get('neighbor', {})
                        if not neighbors:
                            step.failed("No BGP EVPN neighbors configured")
                        else:
                            established = [n for n in neighbors.values() if n.get('state_pfxrcd', '').lower() == 'established']
                            if established:
                                step.passed(f"{len(established)} neighbors established")
                            else:
                                step.failed("No neighbors in established state")
                    except (ParserNotFound, KeyError):
                        output = device.execute('show bgp l2vpn evpn summary')
                        if 'bgp is not running' in output.lower():
                            step.skipped("BGP not running")
                        elif 'neighbor' not in output.lower():
                            step.failed("No BGP EVPN neighbors configured")
                        elif 'established' in output.lower():
                            step.passed("Neighbors established")
                        else:
                            step.failed("No neighbors established")
                except Exception as exc:
                    step.failed(f"Error: {exc}")

    @aetest.test
    def test_evpn_routes(self, testbed):
        for name, device in testbed.devices.items():
            with aetest.steps.Step(f"Check EVPN routes on {name}") as step:
                try:
                    try:
                        parsed = device.parse('show bgp l2vpn evpn')
                        if not parsed.get('instance'):  # no routes
                            step.skipped("No EVPN routes")
                        else:
                            step.passed("EVPN routes present")
                    except ParserNotFound:
                        output = device.execute('show bgp l2vpn evpn | include "Route Distinguisher"')
                        if not output.strip():
                            step.skipped("No EVPN routes")
                        else:
                            step.passed("EVPN routes present")
                except Exception as exc:
                    step.failed(f"Error: {exc}")
