#!/usr/bin/env python3
"""
Custom exceptions for VXLAN test suite

This module defines specific exception classes for better error handling
and more actionable error messages.
"""

from typing import Optional, Dict, Any

class VXLANTestException(Exception):
    """Base exception for VXLAN test suite"""
    
    def __init__(self, message: str, device: Optional[str] = None, 
                 command: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.device = device
        self.command = command
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self) -> str:
        error_msg = self.message
        if self.device:
            error_msg += f" (Device: {self.device})"
        if self.command:
            error_msg += f" (Command: {self.command})"
        if self.details:
            error_msg += f" (Details: {self.details})"
        return error_msg

class DeviceConnectionError(VXLANTestException):
    """Raised when device connection fails"""
    pass

class CommandExecutionError(VXLANTestException):
    """Raised when command execution fails"""
    pass

class ParseError(VXLANTestException):
    """Raised when parsing command output fails"""
    pass

class FeatureNotEnabledError(VXLANTestException):
    """Raised when required VXLAN features are not enabled"""
    
    def __init__(self, feature: str, device: str, enable_command: str):
        self.feature = feature
        self.enable_command = enable_command
        message = f"Feature '{feature}' is not enabled on {device}. Enable with: {enable_command}"
        super().__init__(message, device=device)

class InterfaceDownError(VXLANTestException):
    """Raised when critical interfaces are down"""
    
    def __init__(self, interface: str, device: str, troubleshooting_steps: list):
        self.interface = interface
        self.troubleshooting_steps = troubleshooting_steps
        message = f"Interface {interface} is down on {device}"
        super().__init__(message, device=device, details={'troubleshooting': troubleshooting_steps})

class ConfigurationError(VXLANTestException):
    """Raised when configuration validation fails"""
    
    def __init__(self, component: str, device: str, expected: Any, actual: Any, fix_command: Optional[str] = None):
        self.component = component
        self.expected = expected
        self.actual = actual
        self.fix_command = fix_command
        message = f"{component} configuration error on {device}: expected {expected}, got {actual}"
        details = {'expected': expected, 'actual': actual}
        if fix_command:
            details['fix_command'] = fix_command
        super().__init__(message, device=device, details=details)

class ResourceThresholdError(VXLANTestException):
    """Raised when resource usage exceeds thresholds"""
    
    def __init__(self, resource: str, device: str, current: int, maximum: int, recommendations: list):
        self.resource = resource
        self.current = current
        self.maximum = maximum
        self.recommendations = recommendations
        percentage = (current / maximum) * 100
        message = f"High {resource} usage on {device}: {current}/{maximum} ({percentage:.1f}%)"
        super().__init__(message, device=device, details={
            'current': current,
            'maximum': maximum,
            'percentage': percentage,
            'recommendations': recommendations
        })

class ValidationError(VXLANTestException):
    """Raised when validation checks fail"""
    
    def __init__(self, validation_type: str, device: str, failures: list, suggestions: list):
        self.validation_type = validation_type
        self.failures = failures
        self.suggestions = suggestions
        message = f"{validation_type} validation failed on {device}: {len(failures)} issues found"
        super().__init__(message, device=device, details={
            'failures': failures,
            'suggestions': suggestions
        })

class BGPError(VXLANTestException):
    """Raised when BGP EVPN validation fails"""
    
    def __init__(self, device: str, issue: str, neighbor_states: Dict[str, str], recovery_steps: list):
        self.issue = issue
        self.neighbor_states = neighbor_states
        self.recovery_steps = recovery_steps
        message = f"BGP EVPN issue on {device}: {issue}"
        super().__init__(message, device=device, details={
            'neighbor_states': neighbor_states,
            'recovery_steps': recovery_steps
        })

class PlatformCompatibilityError(VXLANTestException):
    """Raised when platform doesn't support VXLAN"""
    
    def __init__(self, device: str, platform: str, version: str, min_version: str):
        self.platform = platform
        self.version = version
        self.min_version = min_version
        message = f"Platform {platform} version {version} on {device} does not support VXLAN (minimum: {min_version})"
        super().__init__(message, device=device, details={
            'platform': platform,
            'version': version,
            'min_version': min_version
        })
