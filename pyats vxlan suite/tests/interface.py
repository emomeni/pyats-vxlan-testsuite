import logging
import re
from pyats import aetest
from genie.libs.parser.utils.common import ParserNotFound

logger = logging.getLogger(__name__)

class VxlanInterfaceValidation(aetest.Testcase):
    """Verify NVE interface configuration and peers."""

    @aetest.test
    def test_nve_interface_status(self, testbed):
        for name, device in testbed.devices.items():
            with aetest.steps.Step(f"Check NVE interface on {name}") as step:
                try:
                    try:
                        parsed = device.parse('show interface nve1')
                        if parsed['interfaces']['nve1']['oper_state'].lower() != 'up':
                            step.failed("NVE1 interface not up")
                        elif 'source-interface' not in parsed['interfaces']['nve1']['enabled_protocols'].lower():
                            step.failed("NVE1 source interface missing")
                        else:
                            step.passed("NVE1 up and configured")
                    except (ParserNotFound, KeyError):
                        output = device.execute('show interface nve1')
                        if 'line protocol is up' not in output.lower() or 'source-interface' not in output.lower():
                            step.failed("NVE1 interface not properly configured")
                        else:
                            step.passed("NVE1 up and configured")
                except Exception as exc:
                    step.failed(f"Error: {exc}")

    @aetest.test
    def test_nve_peers(self, testbed):
        for name, device in testbed.devices.items():
            with aetest.steps.Step(f"Check NVE peers on {name}") as step:
                try:
                    try:
                        parsed = device.parse('show nve peers')
                        peers = parsed.get('peer_ip', {})
                        if not peers:
                            step.skipped("No NVE peers configured")
                        elif all(p['state'].lower() == 'up' for p in peers.values()):
                            step.passed(f"All {len(peers)} peers up")
                        else:
                            up = sum(1 for p in peers.values() if p['state'].lower() == 'up')
                            step.failed(f"Only {up}/{len(peers)} peers up")
                    except ParserNotFound:
                        output = device.execute('show nve peers')
                        if 'Peer-IP' not in output:
                            step.skipped("No NVE peers configured")
                        else:
                            up = len(re.findall(r'Up', output))
                            total = len(re.findall(r'\d+\.\d+\.\d+\.\d+', output))
                            if total == 0:
                                step.skipped("No peers found")
                            elif up == total:
                                step.passed(f"All {total} peers up")
                            else:
                                step.failed(f"Only {up}/{total} peers up")
                except Exception as exc:
                    step.failed(f"Error: {exc}")
