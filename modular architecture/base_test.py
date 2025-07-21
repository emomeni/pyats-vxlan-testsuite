#!/usr/bin/env python3
"""
Base test classes for enhanced VXLAN test suite

This module provides base classes with common functionality for all test cases,
including structured logging, error handling, and result reporting.
"""

import logging
from typing import Dict, List, Optional, Any
from pyats import aetest
from pyats.log.utils import banner
from vxlan_config import CONFIG, TEST_CATEGORIES
from vxlan_exceptions import *
from vxlan_validators import ValidationResult

logger = logging.getLogger(__name__)

class EnhancedCommonSetup(aetest.CommonSetup):
    """Enhanced common setup with comprehensive device validation"""
    
    @aetest.subsection
    def validate_testbed(self, testbed):
        """Validate testbed configuration"""
        if not testbed.devices:
            self.failed("No devices found in testbed")
        
        logger.info(f"Testbed contains {len(testbed.devices)} devices")
        for device_name in testbed.devices:
            logger.info(f"  - {device_name}")
    
    @aetest.subsection
    def connect_to_devices(self, testbed):
        """Connect to all devices with enhanced error handling"""
        failed_connections = []
        
        for device_name, device in testbed.devices.items():
            try:
                logger.info(banner(f"Connecting to {device_name}"))
                device.connect(learn_hostname=True, init_config_commands=[], init_exec_commands=[])
                logger.info(f"✅ Successfully connected to {device_name}")
                
                # Store device info for later use
                self.parent.parameters.setdefault('device_info', {})[device_name] = {
                    'platform': getattr(device, 'platform', 'unknown'),
                    'os': getattr(device, 'os', 'unknown'),
                    'connected': True
                }
                
            except Exception as e:
                error_msg = f"❌ Failed to connect to {device_name}: {str(e)}"
                logger.error(error_msg)
                failed_connections.append((device_name, str(e)))
                
                self.parent.parameters.setdefault('device_info', {})[device_name] = {
                    'platform': 'unknown',
                    'os': 'unknown', 
                    'connected': False,
                    'error': str(e)
                }
        
        if failed_connections:
            error_summary = "\n".join([f"  - {name}: {error}" for name, error in failed_connections])
            self.failed(f"Failed to connect to {len(failed_connections)} devices:\n{error_summary}")
    
    @aetest.subsection
    def validate_prerequisites(self, testbed):
        """Validate basic prerequisites for VXLAN testing"""
        from vxlan_validators import PlatformValidator
        
        incompatible_devices = []
        
        for device_name, device in testbed.devices.items():
            if not self.parent.parameters['device_info'][device_name]['connected']:
                logger.warning(f"Skipping prerequisite check for {device_name} (not connected)")
                continue
            
            try:
                validator = PlatformValidator(device, device_name)
                result = validator.validate_platform_support()
                
                if not result.passed and result.severity in ['error', 'critical']:
                    incompatible_devices.append((device_name, result.message))
                    logger.error(f"❌ {device_name}: {result.message}")
                else:
                    logger.info(f"✅ {device_name}: {result.message}")
                
            except Exception as e:
                logger.warning(f"Could not validate prerequisites for {device_name}: {str(e)}")
        
        if incompatible_devices:
            error_summary = "\n".join([f"  - {name}: {error}" for name, error in incompatible_devices])
            self.failed(f"Platform compatibility issues found:\n{error_summary}")

class BaseVXLANTest(aetest.Testcase):
    """Base class for all VXLAN test cases"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_results = {}
        self.device_metrics = {}
    
    def setup(self):
        """Common setup for all test cases"""
        self.test_category = getattr(self, 'TEST_CATEGORY', 'unknown')
        category_info = TEST_CATEGORIES.get(self.test_category, {})
        
        logger.info(banner(f"Starting {category_info.get('name', 'VXLAN Test')}"))
        if 'description' in category_info:
            logger.info(f"Description: {category_info['description']}")
    
    def get_connected_devices(self, testbed) -> Dict[str, Any]:
        """Get only connected devices"""
        connected = {}
        device_info = getattr(self.parent.parameters, 'device_info', {})
        
        for device_name, device in testbed.devices.items():
            if device_info.get(device_name, {}).get('connected', False):
                connected[device_name] = device
            else:
                logger.warning(f"Skipping {device_name} - not connected")
        
        return connected
    
    def record_test_result(self, device_name: str, test_name: str, result: ValidationResult):
        """Record test result for reporting"""
        if device_name not in self.test_results:
            self.test_results[device_name] = {}
        
        self.test_results[device_name][test_name] = {
            'passed': result.passed,
            'message': result.message,
            'severity': result.severity,
            'details': result.details,
            'recommendations': result.recommendations
        }
    
    def record_metric(self, device_name: str, metric_name: str, value: Any):
        """Record metric for monitoring"""
        if device_name not in self.device_metrics:
            self.device_metrics[device_name] = {}
        
        self.device_metrics[device_name][metric_name] = value
    
    def process_validation_result(self, step, device_name: str, test_name: str, result: ValidationResult):
        """Process validation result and update test step"""
        self.record_test_result(device_name, test_name, result)
        
        # Log result details
        if result.passed:
            logger.info(f"✅ {device_name}: {result.message}")
            step.passed(result.message)
        else:
            severity_icon = {
                'info': 'ℹ️',
                'warning': '⚠️', 
                'error': '❌',
                'critical': '🚨'
            }.get(result.severity, '❌')
            
            logger.error(f"{severity_icon} {device_name}: {result.message}")
            
            # Add recommendations to failure message
            failure_msg = result.message
            if result.recommendations:
                failure_msg += f"\n\nRecommendations:\n"
                failure_msg += "\n".join([f"  • {rec}" for rec in result.recommendations])
            
            if result.severity == 'critical':
                step.failed(failure_msg)
            elif result.severity == 'error':
                step.failed(failure_msg)
            elif result.severity == 'warning':
                step.failed(failure_msg)  # Still fail but less severe
            else:
                step.skipped(failure_msg)
    
    def cleanup(self):
        """Common cleanup for all test cases"""
        # Log summary of test results
        if self.test_results:
            self._log_test_summary()
        
        # Log metrics
        if self.device_metrics:
            self._log_metrics_summary()
    
    def _log_test_summary(self):
        """Log summary of test results"""
        logger.info(banner("Test Results Summary"))
        
        for device_name, tests in self.test_results.items():
            passed_count = sum(1 for result in tests.values() if result['passed'])
            total_count = len(tests)
            
            logger.info(f"{device_name}: {passed_count}/{total_count} tests passed")
            
            # Log failed tests with recommendations
            failed_tests = {name: result for name, result in tests.items() if not result['passed']}
            if failed_tests:
                logger.info(f"  Failed tests on {device_name}:")
                for test_name, result in failed_tests.items():
                    logger.info(f"    - {test_name}: {result['message']}")
                    if result['recommendations']:
                        logger.info(f"      Recommendations: {', '.join(result['recommendations'][:2])}")
    
    def _log_metrics_summary(self):
        """Log summary of collected metrics"""
        logger.info(banner("Metrics Summary"))
        
        for device_name, metrics in self.device_metrics.items():
            logger.info(f"{device_name} metrics:")
            for metric_name, value in metrics.items():
                logger.info(f"  - {metric_name}: {value}")

class StructuredTestStep:
    """Helper class for structured test steps with consistent error handling"""
    
    def __init__(self, step, device_name: str, test_name: str):
        self.step = step
        self.device_name = device_name
        self.test_name = test_name
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Handle unexpected exceptions
            if isinstance(exc_val, VXLANTestException):
                error_msg = str(exc_val)
                if hasattr(exc_val, 'recommendations') and exc_val.recommendations:
                    error_msg += f"\n\nRecommendations:\n"
                    error_msg += "\n".join([f"  • {rec}" for rec in exc_val.recommendations])
                self.step.failed(error_msg)
            else:
                self.step.failed(f"Unexpected error in {self.test_name}: {str(exc_val)}")
        return True  # Suppress exception propagation
    
    def validate_and_process(self, validator_func, test_instance, *args, **kwargs) -> ValidationResult:
        """Execute validator and process result"""
        try:
            result = validator_func(*args, **kwargs)
            test_instance.process_validation_result(self.step, self.device_name, self.test_name, result)
            return result
        except VXLANTestException as e:
            # Convert to validation result
            result = ValidationResult(
                passed=False,
                message=str(e),
                details=getattr(e, 'details', {}),
                recommendations=getattr(e, 'recommendations', []),
                severity='error'
            )
            test_instance.process_validation_result(self.step, self.device_name, self.test_name, result)
            return result
        except Exception as e:
            # Handle unexpected exceptions
            result = ValidationResult(
                passed=False,
                message=f"Unexpected error: {str(e)}",
                details={'exception_type': type(e).__name__},
                recommendations=["Check device connectivity and configuration"],
                severity='error'
            )
            test_instance.process_validation_result(self.step, self.device_name, self.test_name, result)
            return result

def structured_step(step, device_name: str, test_name: str) -> StructuredTestStep:
    """Helper function to create structured test steps"""
    return StructuredTestStep(step, device_name, test_name)
