#!/usr/bin/env python3

"""
VXLAN Configuration Validation Test Suite for Cisco NX-OS N9K Switches
This comprehensive test suite validates various aspects of VXLAN configuration
"""

import logging
from pyats import aetest
from pyats.log.utils import banner
from genie.libs.parser.utils.common import ParserNotFound
import re

logger = logging.getLogger(__name__)

class CommonSetup(aetest.CommonSetup):
    """Common Setup Section"""
    
    @aetest.subsection
    def connect_to_devices(self, testbed):
        """Connect to all devices in the testbed"""
        for device_name, device in testbed.devices.items():
            logger.info(f"Connecting to device {device_name}")
            try:
                device.connect()
                logger.info(f"Successfully connected to {device_name}")
            except Exception as e:
                self.failed(f"Failed to connect to {device_name}: {str(e)}")
    
    @aetest.subsection
    def check_nxos_version(self, testbed):
        """Verify NX-OS version supports VXLAN"""
        for device_name, device in testbed.devices.items():
            if 'n9k' in device.platform.lower() or 'nexus' in device.platform.lower():
                try:
                    output = device.execute('show version')
                    # Check if running NX-OS 7.0+ which supports VXLAN
                    version_match = re.search(r'system:\s+version\s+(\d+\.\d+)', output)
                    if version_match:
                        version = float(version_match.group(1))
                        if version < 7.0:
                            self.failed(f"{device_name} running NX-OS {version}, VXLAN requires 7.0+")
                        logger.info(f"{device_name} running compatible NX-OS version {version}")
                except Exception as e:
                    logger.warning(f"Could not verify NX-OS version on {device_name}: {str(e)}")

class VxlanFeatureValidation(aetest.Testcase):
    """Test VXLAN feature enablement and basic configuration"""
    
    @aetest.test
    def test_vxlan_feature_enabled(self, testbed):
        """Verify VXLAN feature is enabled"""
        for device_name, device in testbed.devices.items():
            with aetest.steps.Step(f"Check VXLAN feature on {device_name}") as step:
                try:
                    output = device.execute('show feature | include vn-segment')
                    if 'enabled' not in output.lower():
                        step.failed(f"VXLAN feature not enabled on {device_name}")
                    else:
                        step.passed(f"VXLAN feature enabled on {device_name}")
                except Exception as e:
                    step.failed(f"Error checking VXLAN feature on {device_name}: {str(e)}")
    
    @aetest.test
    def test_nve_feature_enabled(self, testbed):
        """Verify NVE (Network Virtualization Edge) feature is enabled"""
        for device_name, device in testbed.devices.items():
            with aetest.steps.Step(f"Check NVE feature on {device_name}") as step:
                try:
                    output = device.execute('show feature | include nv overlay')
                    if 'enabled' not in output.lower():
                        step.failed(f"NVE feature not enabled on {device_name}")
                    else:
                        step.passed(f"NVE feature enabled on {device_name}")
                except Exception as e:
                    step.failed(f"Error checking NVE feature on {device_name}: {str(e)}")

class VxlanInterfaceValidation(aetest.Testcase):
    """Test VXLAN interface configuration and status"""
    
    @aetest.test
    def test_nve_interface_status(self, testbed):
        """Verify NVE interface is up and configured"""
        for device_name, device in testbed.devices.items():
            with aetest.steps.Step(f"Check NVE interface on {device_name}") as step:
                try:
                    # Check NVE interface status
                    output = device.execute('show interface nve1')
                    
                    if 'line protocol is up' not in output.lower():
                        step.failed(f"NVE1 interface not up on {device_name}")
                    
                    # Check for source interface configuration
                    if 'source-interface' not in output.lower():
                        step.failed(f"NVE1 source interface not configured on {device_name}")
                    
                    step.passed(f"NVE1 interface properly configured on {device_name}")
                    
                except Exception as e:
                    step.failed(f"Error checking NVE interface on {device_name}: {str(e)}")
    
    @aetest.test
    def test_nve_peers(self, testbed):
        """Verify NVE peer relationships"""
        for device_name, device in testbed.devices.items():
            with aetest.steps.Step(f"Check NVE peers on {device_name}") as step:
                try:
                    output = device.execute('show nve peers')
                    
                    if 'Peer-IP' not in output:
                        step.skipped(f"No NVE peers configured on {device_name}")
                        continue
                    
                    # Check if peers are up
                    lines = output.split('\n')
                    peer_count = 0
                    up_peers = 0
                    
                    for line in lines:
                        if re.match(r'\d+\.\d+\.\d+\.\d+', line.strip()):
                            peer_count += 1
                            if 'Up' in line:
                                up_peers += 1
                    
                    if peer_count == 0:
                        step.skipped(f"No NVE peers found on {device_name}")
                    elif up_peers == peer_count:
                        step.passed(f"All {peer_count} NVE peers are up on {device_name}")
                    else:
                        step.failed(f"Only {up_peers}/{peer_count} NVE peers are up on {device_name}")
                        
                except Exception as e:
                    step.failed(f"Error checking NVE peers on {device_name}: {str(e)}")

class VxlanVniValidation(aetest.Testcase):
    """Test VXLAN Network Identifier (VNI) configuration"""
    
    @aetest.test
    def test_vni_configuration(self, testbed):
        """Verify VNI to VLAN mappings"""
        for device_name, device in testbed.devices.items():
            with aetest.steps.Step(f"Check VNI configuration on {device_name}") as step:
                try:
                    output = device.execute('show nve vni')
                    
                    if 'VNI' not in output:
                        step.skipped(f"No VNIs configured on {device_name}")
                        continue
                    
                    # Parse VNI information
                    lines = output.split('\n')
                    vni_count = 0
                    
                    for line in lines:
                        if re.search(r'^\s*\d+', line):
                            vni_count += 1
                            # Check if VNI is associated with a VLAN
                            if 'L2' in line and not re.search(r'VLAN:\s*\d+', line):
                                step.failed(f"VNI in line '{line.strip()}' missing VLAN association on {device_name}")
                    
                    if vni_count > 0:
                        step.passed(f"Found {vni_count} properly configured VNIs on {device_name}")
                    else:
                        step.skipped(f"No VNIs found on {device_name}")
                        
                except Exception as e:
                    step.failed(f"Error checking VNI configuration on {device_name}: {str(e)}")
    
    @aetest.test
    def test_vni_ingress_replication(self, testbed):
        """Verify VNI ingress replication configuration"""
        for device_name, device in testbed.devices.items():
            with aetest.steps.Step(f"Check ingress replication on {device_name}") as step:
                try:
                    output = device.execute('show nve vni ingress-replication')
                    
                    if 'VNI' not in output:
                        step.skipped(f"No ingress replication configured on {device_name}")
                        continue
                    
                    # Check for proper ingress replication configuration
                    if 'protocol-bgp' in output.lower() or 'static' in output.lower():
                        step.passed(f"Ingress replication properly configured on {device_name}")
                    else:
                        step.failed(f"Ingress replication not properly configured on {device_name}")
                        
                except Exception as e:
                    step.skipped(f"Ingress replication check not applicable on {device_name}: {str(e)}")

class VxlanL3VniValidation(aetest.Testcase):
    """Test Layer 3 VNI configuration for inter-subnet routing"""
    
    @aetest.test
    def test_l3_vni_configuration(self, testbed):
        """Verify L3 VNI and VRF association"""
        for device_name, device in testbed.devices.items():
            with aetest.steps.Step(f"Check L3 VNI configuration on {device_name}") as step:
                try:
                    output = device.execute('show nve vni')
                    
                    # Look for L3 VNIs
                    l3_vni_found = False
                    lines = output.split('\n')
                    
                    for line in lines:
                        if 'L3' in line and re.search(r'^\s*\d+', line):
                            l3_vni_found = True
                            # Check if L3 VNI has VRF association
                            if not re.search(r'VRF:\s*\w+', line):
                                step.failed(f"L3 VNI missing VRF association: {line.strip()}")
                    
                    if l3_vni_found:
                        step.passed(f"L3 VNIs properly configured with VRF associations on {device_name}")
                    else:
                        step.skipped(f"No L3 VNIs configured on {device_name}")
                        
                except Exception as e:
                    step.failed(f"Error checking L3 VNI configuration on {device_name}: {str(e)}")
    
    @aetest.test
    def test_anycast_gateway(self, testbed):
        """Verify anycast gateway configuration for L3 VNI"""
        for device_name, device in testbed.devices.items():
            with aetest.steps.Step(f"Check anycast gateway on {device_name}") as step:
                try:
                    # Check if anycast gateway MAC is configured
                    output = device.execute('show run | include fabric forwarding anycast-gateway-mac')
                    
                    if not output.strip():
                        step.skipped(f"No anycast gateway MAC configured on {device_name}")
                        continue
                    
                    # Check SVI interfaces for anycast gateway
                    svi_output = device.execute('show ip interface brief vlan')
                    if 'vlan' not in svi_output.lower():
                        step.skipped(f"No SVI interfaces found on {device_name}")
                        continue
                    
                    step.passed(f"Anycast gateway configuration found on {device_name}")
                    
                except Exception as e:
                    step.failed(f"Error checking anycast gateway on {device_name}: {str(e)}")

class VxlanBgpValidation(aetest.Testcase):
    """Test BGP EVPN configuration for VXLAN"""
    
    @aetest.test
    def test_bgp_evpn_configuration(self, testbed):
        """Verify BGP EVPN address family configuration"""
        for device_name, device in testbed.devices.items():
            with aetest.steps.Step(f"Check BGP EVPN configuration on {device_name}") as step:
                try:
                    output = device.execute('show bgp l2vpn evpn summary')
                    
                    if 'bgp is not running' in output.lower():
                        step.skipped(f"BGP not running on {device_name}")
                        continue
                    
                    # Check for EVPN neighbors
                    if 'neighbor' not in output.lower():
                        step.failed(f"No BGP EVPN neighbors configured on {device_name}")
                    else:
                        # Count established neighbors
                        established_count = output.lower().count('established')
                        if established_count > 0:
                            step.passed(f"BGP EVPN has {established_count} established neighbors on {device_name}")
                        else:
                            step.failed(f"No BGP EVPN neighbors in established state on {device_name}")
                            
                except Exception as e:
                    step.failed(f"Error checking BGP EVPN on {device_name}: {str(e)}")
    
    @aetest.test
    def test_evpn_routes(self, testbed):
        """Verify EVPN route advertisements"""
        for device_name, device in testbed.devices.items():
            with aetest.steps.Step(f"Check EVPN routes on {device_name}") as step:
                try:
                    # Check for EVPN type-2 routes (MAC/IP)
                    output = device.execute('show bgp l2vpn evpn | include "Route Distinguisher"')
                    
                    if not output.strip():
                        step.skipped(f"No EVPN routes found on {device_name}")
                        continue
                    
                    # Count route distinguishers
                    rd_count = output.count('Route Distinguisher')
                    if rd_count > 0:
                        step.passed(f"Found {rd_count} EVPN route distinguishers on {device_name}")
                    else:
                        step.failed(f"No EVPN route distinguishers found on {device_name}")
                        
                except Exception as e:
                    step.failed(f"Error checking EVPN routes on {device_name}: {str(e)}")

class VxlanMacAddressValidation(aetest.Testcase):
    """Test VXLAN MAC address learning and forwarding"""
    
    @aetest.test
    def test_mac_address_table(self, testbed):
        """Verify MAC addresses are learned in VXLAN VLANs"""
        for device_name, device in testbed.devices.items():
            with aetest.steps.Step(f"Check VXLAN MAC learning on {device_name}") as step:
                try:
                    # Get VXLAN VLANs first
                    vni_output = device.execute('show nve vni')
                    vxlan_vlans = []
                    
                    for line in vni_output.split('\n'):
                        vlan_match = re.search(r'VLAN:\s*(\d+)', line)
                        if vlan_match:
                            vxlan_vlans.append(vlan_match.group(1))
                    
                    if not vxlan_vlans:
                        step.skipped(f"No VXLAN VLANs found on {device_name}")
                        continue
                    
                    # Check MAC table for VXLAN VLANs
                    mac_learned = False
                    for vlan in vxlan_vlans[:3]:  # Check first 3 VLANs to avoid too much output
                        mac_output = device.execute(f'show mac address-table vlan {vlan}')
                        if re.search(r'[0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4}', mac_output.lower()):
                            mac_learned = True
                            break
                    
                    if mac_learned:
                        step.passed(f"MAC addresses learned in VXLAN VLANs on {device_name}")
                    else:
                        step.failed(f"No MAC addresses learned in VXLAN VLANs on {device_name}")
                        
                except Exception as e:
                    step.failed(f"Error checking MAC address learning on {device_name}: {str(e)}")

class VxlanMulticastValidation(aetest.Testcase):
    """Test multicast configuration for VXLAN (if used)"""
    
    @aetest.test
    def test_multicast_groups(self, testbed):
        """Verify multicast group configuration for VXLAN"""
        for device_name, device in testbed.devices.items():
            with aetest.steps.Step(f"Check multicast configuration on {device_name}") as step:
                try:
                    output = device.execute('show nve multicast')
                    
                    if 'multicast' not in output.lower():
                        step.skipped(f"No multicast configuration for VXLAN on {device_name}")
                        continue
                    
                    # Check if multicast groups are properly configured
                    if re.search(r'\d+\.\d+\.\d+\.\d+', output):
                        step.passed(f"Multicast groups configured for VXLAN on {device_name}")
                    else:
                        step.failed(f"Multicast groups not properly configured on {device_name}")
                        
                except Exception as e:
                    step.skipped(f"Multicast check not applicable on {device_name}: {str(e)}")

class VxlanHealthCheck(aetest.Testcase):
    """Overall VXLAN health and performance checks"""
    
    @aetest.test
    def test_vxlan_statistics(self, testbed):
        """Check VXLAN interface statistics for errors"""
        for device_name, device in testbed.devices.items():
            with aetest.steps.Step(f"Check VXLAN statistics on {device_name}") as step:
                try:
                    output = device.execute('show interface nve1 counters detailed')
                    
                    # Check for error counters
                    error_patterns = ['error', 'drop', 'discard', 'invalid']
                    errors_found = []
                    
                    for line in output.split('\n'):
                        for pattern in error_patterns:
                            if pattern in line.lower() and re.search(r'\d+', line):
                                # Extract number to check if it's non-zero
                                numbers = re.findall(r'\d+', line)
                                if any(int(num) > 0 for num in numbers):
                                    errors_found.append(line.strip())
                    
                    if errors_found:
                        step.failed(f"Errors found in NVE1 statistics on {device_name}: {errors_found}")
                    else:
                        step.passed(f"No errors in NVE1 statistics on {device_name}")
                        
                except Exception as e:
                    step.failed(f"Error checking VXLAN statistics on {device_name}: {str(e)}")
    
    @aetest.test
    def test_vxlan_resource_usage(self, testbed):
        """Check VXLAN resource utilization"""
        for device_name, device in testbed.devices.items():
            with aetest.steps.Step(f"Check VXLAN resources on {device_name}") as step:
                try:
                    # Check VNI usage
                    vni_output = device.execute('show nve vni')
                    vni_count = len([line for line in vni_output.split('\n') if re.match(r'^\s*\d+', line)])
                    
                    # Check if approaching limits (N9K typically supports 16K VNIs)
                    if vni_count > 12000:  # 75% of typical limit
                        step.failed(f"High VNI usage on {device_name}: {vni_count} VNIs configured")
                    elif vni_count > 8000:  # 50% of typical limit
                        step.passed(f"Moderate VNI usage on {device_name}: {vni_count} VNIs configured")
                    else:
                        step.passed(f"Normal VNI usage on {device_name}: {vni_count} VNIs configured")
                        
                except Exception as e:
                    step.failed(f"Error checking VXLAN resources on {device_name}: {str(e)}")

class CommonCleanup(aetest.CommonCleanup):
    """Common Cleanup Section"""
    
    @aetest.subsection
    def disconnect_devices(self, testbed):
        """Disconnect from all devices"""
        for device_name, device in testbed.devices.items():
            logger.info(f"Disconnecting from {device_name}")
            device.disconnect()

if __name__ == '__main__':
    import argparse
    from pyats.topology import loader
    
    parser = argparse.ArgumentParser(description='VXLAN Validation Test Suite')
    parser.add_argument('--testbed', required=True, help='Testbed YAML file')
    
    args = parser.parse_args()
    
    # Load testbed
    testbed = loader.load(args.testbed)
    
    # Run the test
    aetest.main(testbed=testbed)