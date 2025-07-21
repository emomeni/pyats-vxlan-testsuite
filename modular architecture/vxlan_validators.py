#!/usr/bin/env python3
"""
Advanced validation classes for VXLAN components

This module contains specialized validators for different VXLAN components
with comprehensive validation logic and actionable error reporting.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from vxlan_config import CONFIG, REGEX_PATTERNS
from vxlan_exceptions import *
from vxlan_utils import VXLANParser, DeviceExecutor

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result of a validation check"""
    passed: bool
    message: str
    details: Dict[str, Any]
    recommendations: List[str]
    severity: str = 'info'  # info, warning, error, critical

class BaseValidator:
    """Base class for all validators"""
    
    def __init__(self, device, device_name: str):
        self.device = device
        self.device_name = device_name
        self.executor = DeviceExecutor(device, device_name)
        self.parser = VXLANParser()
    
    def create_result(self, passed: bool, message: str, details: Dict[str, Any] = None, 
                     recommendations: List[str] = None, severity: str = 'info') -> ValidationResult:
        """Helper to create validation results"""
        return ValidationResult(
            passed=passed,
            message=message,
            details=details or {},
            recommendations=recommendations or [],
            severity=severity
        )

class PlatformValidator(BaseValidator):
    """Validates platform compatibility and prerequisites"""
    
    def validate_platform_support(self) -> ValidationResult:
        """Validate platform supports VXLAN"""
        try:
            output = self.executor.execute_command(CONFIG.commands.show_version)
            
            # Check if it's a Nexus 9K
            if 'nexus' not in output.lower() or '9000' not in output:
                return self.create_result(
                    passed=False,
                    message=f"Platform may not support VXLAN - expecting Nexus 9000 series",
                    severity='warning',
                    recommendations=[
                        "Verify platform VXLAN support in documentation",
                        "Check hardware capabilities and licensing"
                    ]
                )
            
            # Check NX-OS version
            version = self.parser.parse_nxos_version(output)
            if version is None:
                return self.create_result(
                    passed=False,
                    message="Could not determine NX-OS version",
                    severity='error',
                    recommendations=["Check 'show version' output format"]
                )
            
            if version < 7.0:
                return self.create_result(
                    passed=False,
                    message=f"NX-OS {version} does not support VXLAN (minimum: 7.0)",
                    severity='critical',
                    recommendations=[
                        f"Upgrade NX-OS to version 7.0 or higher",
                        "Current version may have limited VXLAN functionality"
                    ]
                )
            
            return self.create_result(
                passed=True,
                message=f"Platform supports VXLAN (NX-OS {version})",
                details={'version': version, 'platform': 'Nexus 9000'}
            )
            
        except Exception as e:
            return self.create_result(
                passed=False,
                message=f"Platform validation failed: {str(e)}",
                severity='error',
                recommendations=["Check device connectivity and access permissions"]
            )

class FeatureValidator(BaseValidator):
    """Validates VXLAN feature enablement"""
    
    def validate_vxlan_features(self) -> ValidationResult:
        """Validate all required VXLAN features are enabled"""
        try:
            output = self.executor.execute_command(CONFIG.commands.show_feature)
            features = self.parser.parse_feature_status(output)
            
            required_features = {
                CONFIG.features.vn_segment_feature: "feature vn-segment-vlan-based",
                CONFIG.features.nv_overlay_feature: "feature nv overlay"
            }
            
            missing_features = []
            disabled_features = []
            
            for feature, enable_cmd in required_features.items():
                if feature not in features:
                    missing_features.append(feature)
                elif features[feature] != 'enabled':
                    disabled_features.append((feature, enable_cmd))
            
            if missing_features or disabled_features:
                recommendations = []
                error_details = {}
                
                if disabled_features:
                    error_details['disabled'] = disabled_features
                    recommendations.extend([f"Enable with: {cmd}" for _, cmd in disabled_features])
                
                if missing_features:
                    error_details['missing'] = missing_features
                    recommendations.append("Features may not be available on this platform")
                
                return self.create_result(
                    passed=False,
                    message=f"Required VXLAN features not enabled",
                    details=error_details,
                    recommendations=recommendations,
                    severity='critical'
                )
            
            return self.create_result(
                passed=True,
                message="All required VXLAN features are enabled",
                details={'enabled_features': list(required_features.keys())}
            )
            
        except Exception as e:
            return self.create_result(
                passed=False,
                message=f"Feature validation failed: {str(e)}",
                severity='error',
                recommendations=["Check 'show feature' command output"]
            )

class InterfaceValidator(BaseValidator):
    """Validates VXLAN interface configuration and status"""
    
    def validate_nve_interface(self) -> ValidationResult:
        """Validate NVE interface configuration and status"""
        try:
            output = self.executor.execute_command(CONFIG.commands.show_nve_interface)
            
            # Check if interface exists
            if 'invalid interface' in output.lower() or 'not found' in output.lower():
                return self.create_result(
                    passed=False,
                    message="NVE1 interface not configured",
                    severity='critical',
                    recommendations=[
                        "Configure NVE interface: interface nve1",
                        "Add source-interface configuration",
                        "Enable no shutdown"
                    ]
                )
            
            # Check administrative status
            admin_down = 'administratively down' in output.lower()
            if admin_down:
                return self.create_result(
                    passed=False,
                    message="NVE1 interface is administratively down",
                    severity='error',
                    recommendations=[
                        "Enable interface: interface nve1 -> no shutdown"
                    ]
                )
            
            # Check operational status
            line_protocol_up = 'line protocol is up' in output.lower()
            if not line_protocol_up:
                troubleshooting = [
                    "Check source-interface configuration and status",
                    "Verify underlay connectivity",
                    "Check routing to peer devices",
                    "Verify no conflicting configuration"
                ]
                
                return self.create_result(
                    passed=False,
                    message="NVE1 interface line protocol is down",
                    severity='error',
                    recommendations=troubleshooting
                )
            
            # Check source interface configuration
            if 'source-interface' not in output.lower():
                return self.create_result(
                    passed=False,
                    message="NVE1 missing source-interface configuration",
                    severity='error',
                    recommendations=[
                        "Configure source interface: interface nve1 -> source-interface <interface>",
                        "Use loopback interface for stability"
                    ]
                )
            
            # Extract source interface details
            source_match = re.search(r'source-interface:\s*(\S+)', output, re.IGNORECASE)
            source_interface = source_match.group(1) if source_match else "unknown"
            
            return self.create_result(
                passed=True,
                message="NVE1 interface is properly configured and operational",
                details={
                    'source_interface': source_interface,
                    'admin_status': 'up',
                    'oper_status': 'up'
                }
            )
            
        except Exception as e:
            return self.create_result(
                passed=False,
                message=f"NVE interface validation failed: {str(e)}",
                severity='error',
                recommendations=["Check NVE interface configuration"]
            )
    
    def validate_nve_peers(self) -> ValidationResult:
        """Validate NVE peer relationships"""
        try:
            output = self.executor.execute_command(CONFIG.commands.show_nve_peers)
            
            if 'Peer-IP' not in output:
                return self.create_result(
                    passed=True,
                    message="No NVE peers configured (acceptable for single-node deployments)",
                    severity='info',
                    recommendations=[
                        "For multi-node VXLAN, configure peer discovery",
                        "Verify underlay routing for peer reachability"
                    ]
                )
            
            peers = self.parser.parse_nve_peers(output)
            if not peers:
                return self.create_result(
                    passed=False,
                    message="NVE peers table exists but no peers found",
                    severity='warning',
                    recommendations=[
                        "Check underlay connectivity",
                        "Verify VXLAN configuration on peer devices"
                    ]
                )
            
            up_peers = [p for p in peers if p['state'] == 'Up']
            total_peers = len(peers)
            up_count = len(up_peers)
            
            if up_count == 0:
                return self.create_result(
                    passed=False,
                    message=f"All {total_peers} NVE peers are down",
                    details={'peers': peers},
                    severity='critical',
                    recommendations=[
                        "Check underlay routing to peer IPs",
                        "Verify source-interface reachability",
                        "Check for network connectivity issues",
                        "Verify VXLAN configuration on peers"
                    ]
                )
            
            if up_count < total_peers:
                down_peers = [p for p in peers if p['state'] != 'Up']
                return self.create_result(
                    passed=False,
                    message=f"Only {up_count}/{total_peers} NVE peers are up",
                    details={'up_peers': up_peers, 'down_peers': down_peers},
                    severity='error',
                    recommendations=[
                        f"Check connectivity to down peers: {[p['ip'] for p in down_peers]}",
                        "Verify underlay routing",
                        "Check peer device status"
                    ]
                )
            
            return self.create_result(
                passed=True,
                message=f"All {total_peers} NVE peers are up and healthy",
                details={'peers': peers, 'peer_count': total_peers}
            )
            
        except Exception as e:
            return self.create_result(
                passed=False,
                message=f"NVE peer validation failed: {str(e)}",
                severity='error',
                recommendations=["Check NVE peer configuration and connectivity"]
            )

class VNIValidator(BaseValidator):
    """Validates VNI configuration and mappings"""
    
    def validate_vni_configuration(self) -> ValidationResult:
        """Validate VNI to VLAN mappings and configuration"""
        try:
            output = self.executor.execute_command(CONFIG.commands.show_nve_vni)
            
            if 'VNI' not in output:
                return self.create_result(
                    passed=False,
                    message="No VNIs configured",
                    severity='warning',
                    recommendations=[
                        "Configure VNI-to-VLAN mappings",
                        "Example: vlan 100 -> vn-segment 10100",
                        "Add VNI to NVE interface: interface nve1 -> member vni 10100"
                    ]
                )
            
            vnis = self.parser.parse_vni_info(output)
            if not vnis:
                return self.create_result(
                    passed=False,
                    message="VNI section exists but no VNIs parsed",
                    severity='error',
                    recommendations=["Check VNI configuration format"]
                )
            
            # Validate each VNI
            issues = []
            l2_vnis = []
            l3_vnis = []
            
            for vni in vnis:
                if vni.type == 'L2':
                    l2_vnis.append(vni)
                    if vni.vlan is None:
                        issues.append(f"L2 VNI {vni.vni} missing VLAN association")
                elif vni.type == 'L3':
                    l3_vnis.append(vni)
                    if vni.vrf is None:
                        issues.append(f"L3 VNI {vni.vni} missing VRF association")
                
                if vni.state == 'Down':
                    issues.append(f"VNI {vni.vni} is in Down state")
            
            # Check for resource usage
            total_vnis = len(vnis)
            usage_result = self._validate_vni_usage(total_vnis)
            
            if issues:
                return self.create_result(
                    passed=False,
                    message=f"VNI configuration issues found: {len(issues)} problems",
                    details={
                        'issues': issues,
                        'l2_vni_count': len(l2_vnis),
                        'l3_vni_count': len(l3_vnis),
                        'total_vnis': total_vnis
                    },
                    severity='error',
                    recommendations=[
                        "Fix VNI-to-VLAN/VRF mappings",
                        "Check VNI state and troubleshoot down VNIs",
                        "Verify consistent configuration across fabric"
                    ]
                )
            
            recommendations = []
            if not usage_result.passed:
                recommendations.extend(usage_result.recommendations)
            
            return self.create_result(
                passed=usage_result.passed,
                message=f"Found {total_vnis} properly configured VNIs ({len(l2_vnis)} L2, {len(l3_vnis)} L3)",
                details={
                    'l2_vnis': l2_vnis,
                    'l3_vnis': l3_vnis,
                    'total_vnis': total_vnis,
                    'usage_percentage': usage_result.details.get('percentage', 0)
                },
                severity=usage_result.severity,
                recommendations=recommendations
            )
            
        except Exception as e:
            return self.create_result(
                passed=False,
                message=f"VNI validation failed: {str(e)}",
                severity='error',
                recommendations=["Check VNI configuration and command output"]
            )
    
    def _validate_vni_usage(self, current_vnis: int) -> ValidationResult:
        """Validate VNI resource usage"""
        max_vnis = CONFIG.thresholds.max_vni_count
        percentage = (current_vnis / max_vnis) * 100
        
        if percentage >= 90:
            return self.create_result(
                passed=False,
                message=f"Critical VNI usage: {current_vnis}/{max_vnis} ({percentage:.1f}%)",
                details={'percentage': percentage, 'current': current_vnis, 'max': max_vnis},
                severity='critical',
                recommendations=[
                    "Immediate action required - approaching VNI limit",
                    "Review and remove unused VNIs",
                    "Consider VNI consolidation strategies",
                    "Plan for additional hardware if needed"
                ]
            )
        elif percentage >= 75:
            return self.create_result(
                passed=False,
                message=f"High VNI usage: {current_vnis}/{max_vnis} ({percentage:.1f}%)",
                details={'percentage': percentage, 'current': current_vnis, 'max': max_vnis},
                severity='warning',
                recommendations=[
                    "Monitor VNI growth trends",
                    "Plan for capacity expansion",
                    "Optimize VNI allocation"
                ]
            )
        
        return self.create_result(
            passed=True,
            message=f"VNI usage within acceptable limits: {current_vnis}/{max_vnis} ({percentage:.1f}%)",
            details={'percentage': percentage, 'current': current_vnis, 'max': max_vnis}
        )
    
    def validate_ingress_replication(self) -> ValidationResult:
        """Validate ingress replication configuration"""
        try:
            output = self.executor.execute_command(CONFIG.commands.show_nve_vni_ingress)
            
            if 'VNI' not in output:
                return self.create_result(
                    passed=True,
                    message="No specific ingress replication configuration (may use defaults)",
                    severity='info',
                    recommendations=[
                        "Consider configuring explicit ingress replication",
                        "Options: BGP EVPN or static peer lists"
                    ]
                )
            
            # Check for BGP or static configuration
            has_bgp = 'protocol-bgp' in output.lower() or 'bgp' in output.lower()
            has_static = 'static' in output.lower()
            
            if not has_bgp and not has_static:
                return self.create_result(
                    passed=False,
                    message="Ingress replication not properly configured",
                    severity='error',
                    recommendations=[
                        "Configure BGP EVPN for automatic peer discovery",
                        "Or configure static ingress replication lists",
                        "Example: interface nve1 -> member vni 10100 ingress-replication protocol bgp"
                    ]
                )
            
            method = "BGP EVPN" if has_bgp else "Static"
            return self.create_result(
                passed=True,
                message=f"Ingress replication configured using {method}",
                details={'method': method}
            )
            
        except Exception as e:
            return self.create_result(
                passed=True,
                message="Ingress replication check not applicable",
                severity='info',
                recommendations=["Manual verification may be required"]
            )

class BGPValidator(BaseValidator):
    """Validates BGP EVPN configuration"""
    
    def validate_bgp_evpn(self) -> ValidationResult:
        """Validate BGP EVPN configuration and neighbor status"""
        try:
            output = self.executor.execute_command(CONFIG.commands.show_bgp_evpn_summary)
            
            if 'bgp is not running' in output.lower() or 'invalid command' in output.lower():
                return self.create_result(
                    passed=False,
                    message="BGP is not running or EVPN not configured",
                    severity='error',
                    recommendations=[
                        "Enable BGP: feature bgp",
                        "Configure BGP process: router bgp <AS>",
                        "Enable EVPN address family: address-family l2vpn evpn"
                    ]
                )
            
            # Parse neighbor information
            neighbors = self.parser.parse_bgp_neighbors(output)
            if not neighbors:
                return self.create_result(
                    passed=False,
                    message="No BGP EVPN neighbors configured",
                    severity='error',
                    recommendations=[
                        "Configure BGP EVPN neighbors",
                        "Example: neighbor <ip> remote-as <AS>",
                        "Activate EVPN address family for neighbors"
                    ]
                )
            
            # Check neighbor states
            established = [n for n in neighbors if n.state.lower() == 'established']
            total = len(neighbors)
            established_count = len(established)
            
            if established_count == 0:
                return self.create_result(
                    passed=False,
                    message=f"No BGP EVPN neighbors in established state (0/{total})",
                    details={'neighbors': neighbors},
                    severity='critical',
                    recommendations=[
                        "Check BGP neighbor connectivity",
                        "Verify AS numbers and neighbor IPs",
                        "Check routing to neighbor addresses",
                        "Review BGP authentication if configured"
                    ]
                )
            
            if established_count < total:
                down_neighbors = [n for n in neighbors if n.state.lower() != 'established']
                return self.create_result(
                    passed=False,
                    message=f"Only {established_count}/{total} BGP EVPN neighbors established",
                    details={'established': established, 'down': down_neighbors},
                    severity='error',
                    recommendations=[
                        f"Troubleshoot down neighbors: {[n.ip for n in down_neighbors]}",
                        "Check neighbor connectivity and configuration",
                        "Verify BGP timers and authentication"
                    ]
                )
            
            return self.create_result(
                passed=True,
                message=f"All {total} BGP EVPN neighbors are established",
                details={'neighbors': neighbors, 'established_count': established_count}
            )
            
        except Exception as e:
            return self.create_result(
                passed=False,
                message=f"BGP EVPN validation failed: {str(e)}",
                severity='error',
                recommendations=["Check BGP configuration and status"]
            )
    
    def validate_evpn_routes(self) -> ValidationResult:
        """Validate EVPN route advertisements"""
        try:
            output = self.executor.execute_command(CONFIG.commands.show_bgp_evpn_routes + " | include 'Route Distinguisher'")
            
            if not output.strip():
                return self.create_result(
                    passed=False,
                    message="No EVPN routes found",
                    severity='warning',
                    recommendations=[
                        "Check VXLAN VNI configuration",
                        "Verify BGP EVPN route advertisement",
                        "Ensure VNIs are associated with NVE interface"
                    ]
                )
            
            # Count route distinguishers
            rd_count = output.count('Route Distinguisher')
            if rd_count == 0:
                return self.create_result(
                    passed=False,
                    message="No route distinguishers found in EVPN table",
                    severity='error',
                    recommendations=[
                        "Configure route distinguisher for VRFs",
                        "Check EVPN route advertisement configuration"
                    ]
                )
            
            return self.create_result(
                passed=True,
                message=f"Found {rd_count} EVPN route distinguishers",
                details={'rd_count': rd_count}
            )
            
        except Exception as e:
            return self.create_result(
                passed=True,
                message="EVPN route check not applicable or failed",
                severity='info',
                recommendations=["Manual verification may be required"]
            )
