#!/usr/bin/env python3
"""
Utility functions for VXLAN test suite

This module contains helper functions for parsing command outputs,
validating configurations, and performing common operations.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from vxlan_config import REGEX_PATTERNS, CONFIG
from vxlan_exceptions import ParseError, CommandExecutionError

logger = logging.getLogger(__name__)

@dataclass
class VNIInfo:
    """Data class for VNI information"""
    vni: int
    type: str  # L2 or L3
    vlan: Optional[int] = None
    vrf: Optional[str] = None
    state: Optional[str] = None
    replication: Optional[str] = None

@dataclass
class BGPNeighbor:
    """Data class for BGP neighbor information"""
    ip: str
    state: str
    uptime: Optional[str] = None
    prefixes: Optional[int] = None

@dataclass
class InterfaceStatus:
    """Data class for interface status"""
    name: str
    admin_state: str
    oper_state: str
    protocol_state: Optional[str] = None

class VXLANParser:
    """Parser class for VXLAN command outputs"""
    
    @staticmethod
    def parse_nxos_version(output: str) -> Optional[float]:
        """Parse NX-OS version from show version output"""
        try:
            match = re.search(REGEX_PATTERNS['nxos_version'], output)
            if match:
                return float(match.group(1))
            return None
        except Exception as e:
            logger.error(f"Failed to parse NX-OS version: {e}")
            return None
    
    @staticmethod
    def parse_feature_status(output: str) -> Dict[str, str]:
        """Parse feature status from show feature output"""
        features = {}
        try:
            lines = output.split('\n')
            for line in lines:
                match = re.search(REGEX_PATTERNS['feature_status'], line)
                if match:
                    feature_name, status = match.groups()
                    features[feature_name] = status.lower()
        except Exception as e:
            logger.error(f"Failed to parse feature status: {e}")
        return features
    
    @staticmethod
    def parse_nve_peers(output: str) -> List[Dict[str, str]]:
        """Parse NVE peers from show nve peers output"""
        peers = []
        try:
            lines = output.split('\n')
            for line in lines:
                # Look for IP addresses in peer table
                ip_match = re.search(REGEX_PATTERNS['ip_address'], line)
                if ip_match:
                    ip = ip_match.group()
                    # Determine state based on line content
                    state = 'Up' if 'Up' in line else 'Down'
                    peers.append({'ip': ip, 'state': state})
        except Exception as e:
            logger.error(f"Failed to parse NVE peers: {e}")
        return peers
    
    @staticmethod
    def parse_vni_info(output: str) -> List[VNIInfo]:
        """Parse VNI information from show nve vni output"""
        vnis = []
        try:
            lines = output.split('\n')
            current_vni = None
            
            for line in lines:
                # Check for VNI line
                vni_match = re.search(REGEX_PATTERNS['vni_number'], line)
                if vni_match:
                    vni_num = int(vni_match.group(1))
                    vni_type = 'L3' if 'L3' in line else 'L2'
                    current_vni = VNIInfo(vni=vni_num, type=vni_type)
                    
                    # Extract VLAN if present
                    vlan_match = re.search(REGEX_PATTERNS['vlan_number'], line)
                    if vlan_match:
                        current_vni.vlan = int(vlan_match.group(1))
                    
                    # Extract VRF if present
                    vrf_match = re.search(REGEX_PATTERNS['vrf_name'], line)
                    if vrf_match:
                        current_vni.vrf = vrf_match.group(1)
                    
                    # Extract state
                    if 'Up' in line:
                        current_vni.state = 'Up'
                    elif 'Down' in line:
                        current_vni.state = 'Down'
                    
                    vnis.append(current_vni)
                    
        except Exception as e:
            logger.error(f"Failed to parse VNI info: {e}")
        return vnis
    
    @staticmethod
    def parse_bgp_neighbors(output: str) -> List[BGPNeighbor]:
        """Parse BGP neighbors from show bgp l2vpn evpn summary output"""
        neighbors = []
        try:
            lines = output.split('\n')
            for line in lines:
                match = re.search(REGEX_PATTERNS['bgp_neighbor_state'], line)
                if match:
                    ip, state = match.groups()
                    neighbors.append(BGPNeighbor(ip=ip, state=state))
        except Exception as e:
            logger.error(f"Failed to parse BGP neighbors: {e}")
        return neighbors
    
    @staticmethod
    def parse_interface_counters(output: str) -> Dict[str, int]:
        """Parse interface error counters"""
        counters = {}
        try:
            lines = output.split('\n')
            for line in lines:
                match = re.search(REGEX_PATTERNS['error_counter'], line)
                if match:
                    counter_name, count = match.groups()
                    counters[counter_name.strip()] = int(count)
        except Exception as e:
            logger.error(f"Failed to parse interface counters: {e}")
        return counters

class VXLANValidator:
    """Validator class for VXLAN configurations"""
    
    @staticmethod
    def validate_nxos_version(version: Optional[float]) -> Tuple[bool, str]:
        """Validate NX-OS version supports VXLAN"""
        if version is None:
            return False, "Could not determine NX-OS version"
        
        if version < 7.0:
            return False, f"NX-OS {version} does not support VXLAN (minimum: 7.0)"
        
        return True, f"NX-OS {version} supports VXLAN"
    
    @staticmethod
    def validate_required_features(features: Dict[str, str]) -> Tuple[bool, List[str]]:
        """Validate required VXLAN features are enabled"""
        required_features = [
            CONFIG.features.vn_segment_feature,
            CONFIG.features.nv_overlay_feature
        ]
        
        missing_features = []
        for feature in required_features:
            if feature not in features or features[feature] != 'enabled':
                missing_features.append(feature)
        
        is_valid = len(missing_features) == 0
        return is_valid, missing_features
    
    @staticmethod
    def validate_nve_peers(peers: List[Dict[str, str]]) -> Tuple[bool, Dict[str, Any]]:
        """Validate NVE peer status"""
        if not peers:
            return False, {'issue': 'no_peers', 'details': 'No NVE peers configured'}
        
        up_peers = [p for p in peers if p['state'] == 'Up']
        total_peers = len(peers)
        up_count = len(up_peers)
        
        if up_count == 0:
            return False, {
                'issue': 'all_peers_down',
                'details': f'All {total_peers} peers are down',
                'peers': peers
            }
        
        if up_count < total_peers:
            return False, {
                'issue': 'some_peers_down', 
                'details': f'Only {up_count}/{total_peers} peers are up',
                'peers': peers
            }
        
        return True, {
            'issue': None,
            'details': f'All {total_peers} peers are up',
            'peers': peers
        }
    
    @staticmethod
    def validate_vni_configuration(vnis: List[VNIInfo]) -> Tuple[bool, List[str]]:
        """Validate VNI configuration"""
        issues = []
        
        if not vnis:
            issues.append("No VNIs configured")
            return False, issues
        
        for vni in vnis:
            # Check L2 VNI requirements
            if vni.type == 'L2' and vni.vlan is None:
                issues.append(f"L2 VNI {vni.vni} missing VLAN association")
            
            # Check L3 VNI requirements
            if vni.type == 'L3' and vni.vrf is None:
                issues.append(f"L3 VNI {vni.vni} missing VRF association")
            
            # Check VNI state
            if vni.state == 'Down':
                issues.append(f"VNI {vni.vni} is in Down state")
        
        return len(issues) == 0, issues
    
    @staticmethod
    def validate_bgp_evpn(neighbors: List[BGPNeighbor]) -> Tuple[bool, Dict[str, Any]]:
        """Validate BGP EVPN neighbor status"""
        if not neighbors:
            return False, {
                'issue': 'no_neighbors',
                'details': 'No BGP EVPN neighbors configured'
            }
        
        established = [n for n in neighbors if n.state.lower() == 'established']
        total = len(neighbors)
        established_count = len(established)
        
        if established_count == 0:
            return False, {
                'issue': 'no_established_neighbors',
                'details': f'No BGP EVPN neighbors in established state (0/{total})',
                'neighbors': neighbors
            }
        
        if established_count < total:
            return False, {
                'issue': 'some_neighbors_down',
                'details': f'Only {established_count}/{total} BGP EVPN neighbors established',
                'neighbors': neighbors
            }
        
        return True, {
            'issue': None,
            'details': f'All {total} BGP EVPN neighbors established',
            'neighbors': neighbors
        }
    
    @staticmethod
    def validate_resource_usage(resource_type: str, current: int, maximum: int) -> Tuple[bool, Dict[str, Any]]:
        """Validate resource usage against thresholds"""
        percentage = (current / maximum) * 100
        
        # Different thresholds for different resources
        warning_threshold = 75  # 75% by default
        critical_threshold = 90  # 90% by default
        
        if resource_type == 'vni':
            warning_threshold = 70
            critical_threshold = 85
        
        if percentage >= critical_threshold:
            return False, {
                'level': 'critical',
                'percentage': percentage,
                'recommendations': [
                    f"Immediate action required - {resource_type} usage is {percentage:.1f}%",
                    f"Consider capacity planning and optimization",
                    f"Review {resource_type} allocation and remove unused entries"
                ]
            }
        
        if percentage >= warning_threshold:
            return False, {
                'level': 'warning',
                'percentage': percentage,
                'recommendations': [
                    f"Warning - {resource_type} usage is {percentage:.1f}%",
                    f"Plan for capacity expansion",
                    f"Monitor {resource_type} growth trends"
                ]
            }
        
        return True, {
            'level': 'ok',
            'percentage': percentage,
            'recommendations': []
        }

class DeviceExecutor:
    """Helper class for safe device command execution"""
    
    def __init__(self, device, device_name: str):
        self.device = device
        self.device_name = device_name
    
    def execute_command(self, command: str, timeout: int = 30) -> str:
        """Execute command with proper error handling"""
        try:
            logger.debug(f"Executing command on {self.device_name}: {command}")
            output = self.device.execute(command, timeout=timeout)
            logger.debug(f"Command output length: {len(output)} characters")
            return output
        except Exception as e:
            raise CommandExecutionError(
                f"Command execution failed: {str(e)}",
                device=self.device_name,
                command=command
            )
    
    def execute_with_fallback(self, primary_command: str, fallback_commands: List[str]) -> str:
        """Execute command with fallback options"""
        try:
            return self.execute_command(primary_command)
        except CommandExecutionError:
            for fallback_cmd in fallback_commands:
                try:
                    logger.warning(f"Trying fallback command: {fallback_cmd}")
                    return self.execute_command(fallback_cmd)
                except CommandExecutionError:
                    continue
            
            # If all commands failed, raise the original error
            raise CommandExecutionError(
                f"All commands failed including fallbacks",
                device=self.device_name,
                command=primary_command
            )

def safe_int_conversion(value: str, default: int = 0) -> int:
    """Safely convert string to integer"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def format_mac_address(mac: str) -> str:
    """Format MAC address to standard notation"""
    # Remove any separators and convert to lowercase
    clean_mac = re.sub(r'[.:-]', '', mac.lower())
    # Insert dots every 4 characters (Cisco format)
    return f"{clean_mac[0:4]}.{clean_mac[4:8]}.{clean_mac[8:12]}"

def calculate_percentage(current: int, maximum: int) -> float:
    """Calculate percentage with safe division"""
    if maximum == 0:
        return 0.0
    return (current / maximum) * 100

def extract_numbers_from_string(text: str) -> List[int]:
    """Extract all numbers from a string"""
    return [int(match) for match in re.findall(r'\d+', text)]

def is_valid_ip(ip: str) -> bool:
    """Validate IP address format"""
    pattern = r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'
    return bool(re.match(pattern, ip))
