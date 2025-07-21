#!/usr/bin/env python3
"""
Enhanced PyATS VXLAN Test Suite with Improved Error Handling and Code Organization

This comprehensive test suite validates VXLAN configurations on Cisco NX-OS N9K switches
with enhanced error handling, structured validation, and actionable reporting.

Version: 2.0.0
Author: Enhanced PyATS Team
"""

import logging
from typing import Dict, List, Optional, Any
from pyats import aetest
from pyats.log.utils import banner
from base_test import EnhancedCommonSetup, BaseVXLANTest, structured_step
from vxlan_validators import *
from vxlan_config import CONFIG
from vxlan_exceptions import *

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CommonSetup(EnhancedCommonSetup):
    """Enhanced common setup for VXLAN test suite"""
    pass

class VXLANPrerequisiteValidation(BaseVXLANTest):
    """Comprehensive prerequisite validation for VXLAN testing"""
    
    TEST_CATEGORY = 'prerequisites'
    
    @aetest.test
    def test_platform_compatibility(self, testbed):
        """Validate platform supports VXLAN and has compatible NX-OS version"""
        connected_devices = self.get_connected_devices(testbed)
        
        for device_name, device in connected_devices.items():
            with aetest.steps.Step(f"Platform compatibility check for {device_name}") as step:
                with structured_step(step, device_name, "platform_compatibility") as s:
                    validator = PlatformValidator(device, device_name)
                    result = s.validate_and_process(validator.validate_platform_support, self)
                    
                    # Record platform metrics
                    if 'version' in result.details:
                        self.record_metric(device_name, 'nxos_version', result.details['version'])
                    if 'platform' in result.details:
                        self.record_metric(device_name, 'platform', result.details['platform'])
    
    @aetest.test
    def test_required_features(self, testbed):
        """Validate all required VXLAN features are enabled"""
        connected_devices = self.get_connected_devices(testbed)
        
        for device_name, device in connected_devices.items():
            with aetest.steps.Step(f"Feature validation for {device_name}") as step:
                with structured_step(step, device_name, "required_features") as s:
                    validator = FeatureValidator(device, device_name)
                    result = s.validate_and_process(validator.validate_vxlan_features, self)
                    
                    # Record enabled features
                    if 'enabled_features' in result.details:
                        self.record_metric(device_name, 'enabled_features', result.details['enabled_features'])

class VXLANInterfaceValidation(BaseVXLANTest):
    """Enhanced NVE interface and peer validation"""
    
    TEST_CATEGORY = 'interfaces'
    
    @aetest.test
    def test_nve_interface_status(self, testbed):
        """Comprehensive NVE interface validation"""
        connected_devices = self.get_connected_devices(testbed)
        
        for device_name, device in connected_devices.items():
            with aetest.steps.Step(f"NVE interface validation for {device_name}") as step:
                with structured_step(step, device_name, "nve_interface_status") as s:
                    validator = InterfaceValidator(device, device_name)
                    result = s.validate_and_process(validator.validate_nve_interface, self)
                    
                    # Record interface metrics
                    if result.passed and 'source_interface' in result.details:
                        self.record_metric(device_name, 'nve_source_interface', result.details['source_interface'])
    
    @aetest.test
    def test_nve_peer_relationships(self, testbed):
        """Validate NVE peer connectivity and status"""
        connected_devices = self.get_connected_devices(testbed)
        
        for device_name, device in connected_devices.items():
            with aetest.steps.Step(f"NVE peer validation for {device_name}") as step:
                with structured_step(step, device_name, "nve_peer_relationships") as s:
                    validator = InterfaceValidator(device, device_name)
                    result = s.validate_and_process(validator.validate_nve_peers, self)
                    
                    # Record peer metrics
                    if 'peer_count' in result.details:
                        self.record_metric(device_name, 'nve_peer_count', result.details['peer_count'])
                    if 'peers' in result.details:
                        up_peers = len([p for p in result.details['peers'] if p.get('state') == 'Up'])
                        self.record_metric(device_name, 'nve_peers_up', up_peers)

class VXLANVNIValidation(BaseVXLANTest):
    """Enhanced VNI configuration and mapping validation"""
    
    TEST_CATEGORY = 'vnis'
    
    @aetest.test
    def test_vni_configuration(self, testbed):
        """Comprehensive VNI-to-VLAN mapping validation"""
        connected_devices = self.get_connected_devices(testbed)
        
        for device_name, device in connected_devices.items():
            with aetest.steps.Step(f"VNI configuration validation for {device_name}") as step:
                with structured_step(step, device_name, "vni_configuration") as s:
                    validator = VNIValidator(device, device_name)
                    result = s.validate_and_process(validator.validate_vni_configuration, self)
                    
                    # Record VNI metrics
                    if 'total_vnis' in result.details:
                        self.record_metric(device_name, 'total_vnis', result.details['total_vnis'])
                    if 'l2_vni_count' in result.details:
                        self.record_metric(device_name, 'l2_vnis', result.details['l2_vni_count'])
                    if 'l3_vni_count' in result.details:
                        self.record_metric(device_name, 'l3_vnis', result.details['l3_vni_count'])
                    if 'usage_percentage' in result.details:
                        self.record_metric(device_name, 'vni_usage_percent', result.details['usage_percentage'])
    
    @aetest.test
    def test_ingress_replication(self, testbed):
        """Validate VNI ingress replication configuration"""
        connected_devices = self.get_connected_devices(testbed)
        
        for device_name, device in connected_devices.items():
            with aetest.steps.Step(f"Ingress replication validation for {device_name}") as step:
                with structured_step(step, device_name, "ingress_replication") as s:
                    validator = VNIValidator(device, device_name)
                    result = s.validate_and_process(validator.validate_ingress_replication, self)
                    
                    # Record replication method
                    if 'method' in result.details:
                        self.record_metric(device_name, 'replication_method', result.details['method'])

class VXLANBGPEVPNValidation(BaseVXLANTest):
    """Enhanced BGP EVPN control plane validation"""
    
    TEST_CATEGORY = 'bgp_evpn'
    
    @aetest.test
    def test_bgp_evpn_neighbors(self, testbed):
        """Comprehensive BGP EVPN neighbor validation"""
        connected_devices = self.get_connected_devices(testbed)
        
        for device_name, device in connected_devices.items():
            with aetest.steps.Step(f"BGP EVPN neighbor validation for {device_name}") as step:
                with structured_step(step, device_name, "bgp_evpn_neighbors") as s:
                    validator = BGPValidator(device, device_name)
                    result = s.validate_and_process(validator.validate_bgp_evpn, self)
                    
                    # Record BGP metrics
                    if 'established_count' in result.details:
                        self.record_metric(device_name, 'bgp_evpn_neighbors', result.details['established_count'])
    
    @aetest.test 
    def test_evpn_route_advertisements(self, testbed):
        """Validate EVPN route advertisements and RDs"""
        connected_devices = self.get_connected_devices(testbed)
        
        for device_name, device in connected_devices.items():
            with aetest.steps.Step(f"EVPN route validation for {device_name}") as step:
                with structured_step(step, device_name, "evpn_route_advertisements") as s:
                    validator = BGPValidator(device, device_name)
                    result = s.validate_and_process(validator.validate_evpn_routes, self)
                    
                    # Record route metrics
                    if 'rd_count' in result.details:
                        self.record_metric(device_name, 'evpn_route_distinguishers', result.details['rd_count'])

class VXLANDataPlaneValidation(BaseVXLANTest):
    """Data plane validation for MAC learning and forwarding"""
    
    TEST_CATEGORY = 'data_plane'
    
    @aetest.test
    def test_mac_address_learning(self, testbed):
        """Validate MAC address learning in VXLAN VLANs"""
        connected_devices = self.get_connected_devices(testbed)
        
        for device_name, device in connected_devices.items():
            with aetest.steps.Step(f"MAC learning validation for {device_name}") as step:
                try:
                    # Get VXLAN VLANs
                    vni_output = device.execute(CONFIG.commands.show_nve_vni)
                    vxlan_vlans = []
                    
                    for line in vni_output.split('\n'):
                        vlan_match = re.search(r'VLAN:\s*(\d+)', line)
                        if vlan_match:
                            vxlan_vlans.append(vlan_match.group(1))
                    
                    if not vxlan_vlans:
                        step.skipped(f"No VXLAN VLANs found on {device_name}")
                        continue
                    
                    # Check MAC learning in first few VLANs
                    mac_learned = False
                    checked_vlans = []
                    
                    for vlan in vxlan_vlans[:3]:  # Check first 3 VLANs
                        try:
                            mac_output = device.execute(f'show mac address-table vlan {vlan}')
                            if re.search(r'[0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4}', mac_output.lower()):
                                mac_learned = True
                                checked_vlans.append(vlan)
                        except Exception as e:
                            logger.warning(f"Could not check MAC table for VLAN {vlan}: {e}")
                    
                    if mac_learned:
                        step.passed(f"MAC addresses learned in VXLAN VLANs on {device_name}")
                        self.record_metric(device_name, 'mac_learning_vlans', checked_vlans)
                    else:
                        step.failed(f"No MAC addresses learned in VXLAN VLANs on {device_name}")
                
                except Exception as e:
                    step.failed(f"MAC learning validation failed on {device_name}: {str(e)}")

class VXLANHealthMonitoring(BaseVXLANTest):
    """Enhanced health monitoring and performance validation"""
    
    TEST_CATEGORY = 'health'
    
    @aetest.test
    def test_interface_statistics(self, testbed):
        """Monitor NVE interface statistics for errors"""
        connected_devices = self.get_connected_devices(testbed)
        
        for device_name, device in connected_devices.items():
            with aetest.steps.Step(f"Interface statistics check for {device_name}") as step:
                try:
                    output = device.execute(CONFIG.commands.show_nve_counters)
                    
                    # Parse error counters
                    error_patterns = ['error', 'drop', 'discard', 'invalid']
                    errors_found = []
                    total_errors = 0
                    
                    for line in output.split('\n'):
                        for pattern in error_patterns:
                            if pattern in line.lower() and re.search(r'\d+', line):
                                numbers = re.findall(r'\d+', line)
                                if any(int(num) > CONFIG.thresholds.error_counter_threshold for num in numbers):
                                    errors_found.append(line.strip())
                                    total_errors += sum(int(num) for num in numbers if int(num) > 0)
                    
                    self.record_metric(device_name, 'nve_error_count', total_errors)
                    
                    if errors_found:
                        error_msg = f"High error counters found on {device_name}:\n"
                        error_msg += "\n".join([f"  • {error}" for error in errors_found[:5]])
                        if len(errors_found) > 5:
                            error_msg += f"\n  • ... and {len(errors_found) - 5} more"
                        
                        error_msg += f"\n\nRecommendations:\n"
                        error_msg += "  • Check physical connectivity and cables\n"
                        error_msg += "  • Verify underlay network stability\n"
                        error_msg += "  • Review VXLAN configuration for inconsistencies"
                        
                        step.failed(error_msg)
                    else:
                        step.passed(f"No significant errors in NVE statistics on {device_name}")
                
                except Exception as e:
                    step.failed(f"Statistics check failed on {device_name}: {str(e)}")
    
    @aetest.test
    def test_resource_utilization(self, testbed):
        """Monitor VXLAN resource utilization and capacity"""
        connected_devices = self.get_connected_devices(testbed)
        
        for device_name, device in connected_devices.items():
            with aetest.steps.Step(f"Resource utilization check for {device_name}") as step:
                try:
                    # Check VNI usage
                    vni_output = device.execute(CONFIG.commands.show_nve_vni)
                    vni_count = len([line for line in vni_output.split('\n') 
                                   if re.match(r'^\s*\d+', line)])
                    
                    self.record_metric(device_name, 'current_vni_count', vni_count)
                    
                    # Validate against thresholds
                    max_vnis = CONFIG.thresholds.max_vni_count
                    percentage = (vni_count / max_vnis) * 100
                    
                    self.record_metric(device_name, 'vni_utilization_percent', round(percentage, 2))
                    
                    if percentage >= 90:
                        step.failed(
                            f"Critical VNI usage on {device_name}: {vni_count}/{max_vnis} ({percentage:.1f}%)\n\n"
                            f"Recommendations:\n"
                            f"  • Immediate action required - approaching VNI limit\n"
                            f"  • Review and remove unused VNIs\n"
                            f"  • Consider VNI consolidation strategies\n"
                            f"  • Plan for additional hardware if needed"
                        )
                    elif percentage >= 75:
                        step.failed(
                            f"High VNI usage on {device_name}: {vni_count}/{max_vnis} ({percentage:.1f}%)\n\n"
                            f"Recommendations:\n"
                            f"  • Monitor VNI growth trends\n"
                            f"  • Plan for capacity expansion\n"
                            f"  • Optimize VNI allocation"
                        )
                    else:
                        step.passed(
                            f"VNI usage within acceptable limits on {device_name}: "
                            f"{vni_count}/{max_vnis} ({percentage:.1f}%)"
                        )
                
                except Exception as e:
                    step.failed(f"Resource utilization check failed on {device_name}: {str(e)}")

class VXLANMulticastValidation(BaseVXLANTest):
    """Multicast configuration validation (if applicable)"""
    
    TEST_CATEGORY = 'multicast'
    
    @aetest.test
    def test_multicast_configuration(self, testbed):
        """Validate multicast configuration for VXLAN (if used)"""
        connected_devices = self.get_connected_devices(testbed)
        
        for device_name, device in connected_devices.items():
            with aetest.steps.Step(f"Multicast validation for {device_name}") as step:
                try:
                    output = device.execute(CONFIG.commands.show_nve_multicast)
                    
                    if 'multicast' not in output.lower():
                        step.skipped(f"No multicast configuration for VXLAN on {device_name}")
                        continue
                    
                    # Check if multicast groups are properly configured
                    if re.search(r'\d+\.\d+\.\d+\.\d+', output):
                        step.passed(f"Multicast groups configured for VXLAN on {device_name}")
                        # Extract and record multicast groups
                        groups = re.findall(r'\d+\.\d+\.\d+\.\d+', output)
                        self.record_metric(device_name, 'multicast_groups', groups)
                    else:
                        step.failed(f"Multicast groups not properly configured on {device_name}")
                
                except Exception as e:
                    step.skipped(f"Multicast check not applicable on {device_name}: {str(e)}")

class CommonCleanup(aetest.CommonCleanup):
    """Enhanced common cleanup with comprehensive reporting"""
    
    @aetest.subsection
    def generate_summary_report(self, testbed):
        """Generate comprehensive test summary report"""
        logger.info(banner("VXLAN Test Suite Summary Report"))
        
        # Collect all test results from test classes
        all_results = {}
        all_metrics = {}
        
        # Get results from each test class
        for test_name in ['VXLANPrerequisiteValidation', 'VXLANInterfaceValidation', 
                         'VXLANVNIValidation', 'VXLANBGPEVPNValidation', 
                         'VXLANDataPlaneValidation', 'VXLANHealthMonitoring']:
            if hasattr(self.parent, test_name.lower()):
                test_instance = getattr(self.parent, test_name.lower())
                if hasattr(test_instance, 'test_results'):
                    all_results.update(test_instance.test_results)
                if hasattr(test_instance, 'device_metrics'):
                    for device, metrics in test_instance.device_metrics.items():
                        if device not in all_metrics:
                            all_metrics[device] = {}
                        all_metrics[device].update(metrics)
        
        # Generate per-device summary
        for device_name in testbed.devices:
            logger.info(f"\n{'='*50}")
            logger.info(f"Device: {device_name}")
            logger.info(f"{'='*50}")
            
            device_results = all_results.get(device_name, {})
            if device_results:
                passed_tests = [name for name, result in device_results.items() if result['passed']]
                failed_tests = [name for name, result in device_results.items() if not result['passed']]
                
                logger.info(f"Test Results: {len(passed_tests)} passed, {len(failed_tests)} failed")
                
                if failed_tests:
                    logger.info("\nFailed Tests:")
                    for test_name in failed_tests:
                        result = device_results[test_name]
                        logger.info(f"  ❌ {test_name}: {result['message']}")
                        if result['recommendations']:
                            logger.info(f"     Recommendations: {', '.join(result['recommendations'][:2])}")
                
                if passed_tests:
                    logger.info(f"\nPassed Tests: {', '.join(passed_tests)}")
            
            # Show key metrics
            device_metrics = all_metrics.get(device_name, {})
            if device_metrics:
                logger.info("\nKey Metrics:")
                for metric, value in device_metrics.items():
                    logger.info(f"  • {metric}: {value}")
        
        # Overall summary
        total_devices = len(testbed.devices)
        healthy_devices = len([d for d in testbed.devices if not any(
            not result['passed'] and result['severity'] in ['error', 'critical'] 
            for result in all_results.get(d, {}).values()
        )])
        
        logger.info(f"\n{'='*60}")
        logger.info(f"OVERALL SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Total Devices: {total_devices}")
        logger.info(f"Healthy Devices: {healthy_devices}")
        logger.info(f"Devices with Issues: {total_devices - healthy_devices}")
        
        if healthy_devices == total_devices:
            logger.info("🎉 All devices passed VXLAN validation!")
        else:
            logger.info("⚠️  Some devices require attention. Review failed tests above.")
    
    @aetest.subsection
    def disconnect_devices(self, testbed):
        """Cleanly disconnect from all devices"""
        for device_name, device in testbed.devices.items():
            try:
                if device.connected:
                    device.disconnect()
                    logger.info(f"Disconnected from {device_name}")
            except Exception as e:
                logger.warning(f"Error disconnecting from {device_name}: {e}")

# Main execution point
if __name__ == '__main__':
    import argparse
    from pyats.easypy import run
    
    parser = argparse.ArgumentParser(description='Enhanced VXLAN Test Suite')
    parser.add_argument('--testbed', required=True, help='Path to testbed YAML file')
    parser.add_argument('--loglevel', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
    parser.add_argument('--html-logs', help='Directory for HTML log output')
    
    args = parser.parse_args()
    
    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.loglevel))
    
    # Run the test suite
    run(testscript=__file__, testbed=args.testbed, loglevel=args.loglevel)
