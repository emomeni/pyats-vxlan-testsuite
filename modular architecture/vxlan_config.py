#!/usr/bin/env python3
"""
VXLAN Test Suite Configuration Constants and Settings

This module contains all configuration constants, thresholds, and settings
used throughout the VXLAN test suite.
"""

from typing import Dict, List, Any
from dataclasses import dataclass
import os

@dataclass
class VXLANThresholds:
    """VXLAN performance and capacity thresholds"""
    max_vni_count: int = 12000  # 75% of typical N9K limit (16K)
    max_peer_count: int = 500
    error_counter_threshold: int = 100
    bgp_neighbor_timeout: int = 300  # seconds
    interface_up_timeout: int = 60   # seconds

@dataclass
class VXLANFeatures:
    """Required VXLAN features and their expected states"""
    vn_segment_feature: str = "vn-segment-vlan-based"
    nv_overlay_feature: str = "nv overlay"
    bgp_feature: str = "bgp"
    evpn_feature: str = "evpn"

@dataclass
class VXLANCommands:
    """Standard VXLAN show commands"""
    show_version: str = "show version"
    show_feature: str = "show feature"
    show_nve_interface: str = "show interface nve1"
    show_nve_peers: str = "show nve peers"
    show_nve_vni: str = "show nve vni"
    show_nve_vni_ingress: str = "show nve vni ingress-replication"
    show_nve_multicast: str = "show nve multicast"
    show_bgp_evpn_summary: str = "show bgp l2vpn evpn summary"
    show_bgp_evpn_routes: str = "show bgp l2vpn evpn"
    show_mac_address_table: str = "show mac address-table"
    show_nve_counters: str = "show interface nve1 counters detailed"
    show_running_config: str = "show running-config"

class VXLANConfig:
    """Main configuration class for VXLAN test suite"""
    
    def __init__(self):
        self.thresholds = VXLANThresholds()
        self.features = VXLANFeatures()
        self.commands = VXLANCommands()
        
        # Environment-based configuration overrides
        self._load_env_overrides()
    
    def _load_env_overrides(self) -> None:
        """Load configuration overrides from environment variables"""
        # Threshold overrides
        if os.getenv("VXLAN_MAX_VNI_COUNT"):
            self.thresholds.max_vni_count = int(os.getenv("VXLAN_MAX_VNI_COUNT"))
        
        if os.getenv("VXLAN_MAX_PEER_COUNT"):
            self.thresholds.max_peer_count = int(os.getenv("VXLAN_MAX_PEER_COUNT"))
        
        if os.getenv("VXLAN_ERROR_THRESHOLD"):
            self.thresholds.error_counter_threshold = int(os.getenv("VXLAN_ERROR_THRESHOLD"))

# Global configuration instance
CONFIG = VXLANConfig()

# Regex patterns for parsing command outputs
REGEX_PATTERNS = {
    'nxos_version': r'system:\s+version\s+(\d+\.\d+)',
    'ip_address': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
    'mac_address': r'[0-9a-fA-F]{4}\.[0-9a-fA-F]{4}\.[0-9a-fA-F]{4}',
    'vni_number': r'^\s*(\d+)',
    'vlan_number': r'VLAN:\s*(\d+)',
    'vrf_name': r'VRF:\s*(\w+)',
    'route_distinguisher': r'Route Distinguisher:\s*(\d+:\d+)',
    'bgp_neighbor_state': r'(\d+\.\d+\.\d+\.\d+)\s+\d+\s+\d+\s+\d+\s+\d+\s+(\w+)',
    'feature_status': r'(\w+(?:-\w+)*)\s+\d+\s+(\w+)',
    'interface_status': r'(\w+\d+(?:/\d+)*)\s+(\w+)\s+(\w+)',
    'error_counter': r'(\w+(?:\s+\w+)*)\s*:\s*(\d+)',
}

# Error message templates
ERROR_MESSAGES = {
    'connection_failed': "Failed to connect to device {device}: {error}",
    'command_failed': "Command '{command}' failed on {device}: {error}",
    'feature_disabled': "Feature '{feature}' is not enabled on {device}. Enable with 'feature {feature}'",
    'interface_down': "Interface {interface} is down on {device}. Check configuration and physical connectivity",
    'no_peers': "No NVE peers found on {device}. Verify underlay connectivity and VXLAN configuration",
    'peers_down': "Only {up}/{total} NVE peers are up on {device}. Check peer connectivity",
    'no_vnis': "No VNIs configured on {device}. Configure VNI-to-VLAN mappings",
    'vni_misconfigured': "VNI {vni} is misconfigured on {device}: {issue}",
    'bgp_not_running': "BGP is not running on {device}. Start BGP process",
    'no_bgp_neighbors': "No BGP EVPN neighbors configured on {device}",
    'bgp_neighbors_down': "BGP EVPN neighbors not established on {device}",
    'high_resource_usage': "High {resource} usage on {device}: {current}/{max} ({percentage}%)",
    'parsing_error': "Failed to parse {command} output on {device}: {error}",
    'validation_error': "Validation failed for {component} on {device}: {details}",
}

# Success message templates
SUCCESS_MESSAGES = {
    'feature_enabled': "Feature '{feature}' is properly enabled on {device}",
    'interface_up': "Interface {interface} is up and operational on {device}",
    'peers_healthy': "All {count} NVE peers are up and healthy on {device}",
    'vnis_configured': "Found {count} properly configured VNIs on {device}",
    'bgp_healthy': "BGP EVPN has {count} established neighbors on {device}",
    'no_errors': "No errors found in {component} on {device}",
    'resource_usage_ok': "{resource} usage is within acceptable limits on {device}: {current}/{max}",
}

# Test categories and their descriptions
TEST_CATEGORIES = {
    'prerequisites': {
        'name': 'Prerequisites Validation',
        'description': 'Validate basic connectivity and platform compatibility'
    },
    'features': {
        'name': 'Feature Validation', 
        'description': 'Verify VXLAN and NVE features are enabled'
    },
    'interfaces': {
        'name': 'Interface Validation',
        'description': 'Check NVE interface status and configuration'
    },
    'vnis': {
        'name': 'VNI Validation',
        'description': 'Validate VNI-to-VLAN mappings and configuration'
    },
    'l3_vnis': {
        'name': 'Layer 3 VNI Validation',
        'description': 'Check L3 VNI and VRF associations'
    },
    'bgp_evpn': {
        'name': 'BGP EVPN Validation',
        'description': 'Verify BGP EVPN control plane functionality'
    },
    'data_plane': {
        'name': 'Data Plane Validation',
        'description': 'Check MAC learning and forwarding'
    },
    'multicast': {
        'name': 'Multicast Validation',
        'description': 'Validate multicast configuration (if applicable)'
    },
    'health': {
        'name': 'Health and Performance',
        'description': 'Monitor statistics and resource usage'
    }
}
