# VXLAN Configuration Validation Test Suite

A comprehensive automated test suite for validating VXLAN (Virtual Extensible LAN) configurations on Cisco NX-OS N9K switches using the pyATS framework.

## Overview

This test suite provides automated validation of VXLAN overlay network configurations, ensuring proper setup and functionality of VXLAN components including NVE interfaces, VNI mappings, BGP EVPN, and associated networking features.

## Features

- **Complete VXLAN Validation**: Tests all major VXLAN components and configurations
- **Multi-Device Support**: Validates configurations across multiple switches in a testbed
- **Comprehensive Reporting**: Detailed test results with pass/fail/skip status
- **Error Detection**: Identifies configuration issues and performance problems
- **Resource Monitoring**: Tracks VNI usage and system resource utilization
- **BGP EVPN Integration**: Validates BGP EVPN control plane functionality

## Prerequisites

### Software Requirements

```bash
# Core Dependencies
pip install pyats[full]
pip install genie
```

### Hardware Requirements

- Cisco Nexus 9000 series switches
- NX-OS version 7.0 or higher
- VXLAN feature licensing (if applicable)

### Network Requirements

- Management connectivity to all devices
- SSH/NETCONF access configured
- Proper device credentials

## Installation

1. **Clone or download the test suite:**
```bash
# Save the test suite as vxlan_validation.py
wget <your-repo>/vxlan_validation.py
chmod +x vxlan_validation.py
```

2. **Install dependencies:**
```bash
pip install pyats[full] genie
```

3. **Create testbed file (see Configuration section)**

## Configuration

### Testbed Configuration

Create a YAML testbed file (`testbed.yaml`) defining your network devices:

```yaml
testbed:
  name: VXLAN_Testbed
  
devices:
  leaf1:
    type: switch
    os: nxos
    platform: n9k
    credentials:
      default:
        username: admin
        password: admin
    connections:
      cli:
        protocol: ssh
        ip: 192.168.1.10
        
  leaf2:
    type: switch
    os: nxos
    platform: n9k
    credentials:
      default:
        username: admin
        password: admin
    connections:
      cli:
        protocol: ssh
        ip: 192.168.1.11
        
  spine1:
    type: switch
    os: nxos
    platform: n9k
    credentials:
      default:
        username: admin
        password: admin
    connections:
      cli:
        protocol: ssh
        ip: 192.168.1.20
```

## Usage

### Basic Execution

```bash
python vxlan_validation.py --testbed testbed.yaml
```

### Advanced Usage

```bash
# Run with specific log level
python vxlan_validation.py --testbed testbed.yaml --loglevel INFO

# Run specific test classes only
python vxlan_validation.py --testbed testbed.yaml --testcase VxlanFeatureValidation

# Generate detailed HTML report
python vxlan_validation.py --testbed testbed.yaml --html-logs ./reports/
```

## Test Categories

### 1. Feature Validation (`VxlanFeatureValidation`)
- **VXLAN Feature Status**: Verifies `feature vn-segment-vlan-based` is enabled
- **NVE Feature Status**: Confirms `feature nv overlay` is enabled

### 2. Interface Validation (`VxlanInterfaceValidation`)
- **NVE Interface Status**: Checks NVE1 interface operational state
- **Source Interface**: Validates source-interface configuration
- **Peer Relationships**: Verifies NVE peer connectivity and status

### 3. VNI Validation (`VxlanVniValidation`)
- **VNI-to-VLAN Mapping**: Confirms proper Layer 2 VNI associations
- **Ingress Replication**: Validates replication methods (BGP/Static)
- **VNI Configuration**: Checks VNI operational parameters

### 4. Layer 3 VNI Validation (`VxlanL3VniValidation`)
- **L3 VNI Configuration**: Verifies L3 VNI and VRF associations
- **Anycast Gateway**: Validates anycast gateway MAC configuration
- **SVI Interfaces**: Checks SVI interface configurations

### 5. BGP EVPN Validation (`VxlanBgpValidation`)
- **BGP EVPN Configuration**: Verifies BGP L2VPN EVPN address family
- **Neighbor Relationships**: Checks BGP EVPN neighbor states
- **Route Advertisement**: Validates EVPN route advertisements and RDs

### 6. MAC Learning Validation (`VxlanMacAddressValidation`)
- **MAC Address Tables**: Verifies MAC learning in VXLAN VLANs
- **Remote MAC Entries**: Checks remote MAC address learning

### 7. Multicast Validation (`VxlanMulticastValidation`)
- **Multicast Groups**: Validates multicast group configurations (if used)
- **Multicast Forwarding**: Checks multicast forwarding for BUM traffic

### 8. Health Monitoring (`VxlanHealthCheck`)
- **Interface Statistics**: Monitors NVE interface counters for errors
- **Resource Usage**: Tracks VNI utilization and capacity planning
- **Performance Metrics**: Identifies potential performance issues

## Test Results

### Result Interpretation

- **✅ PASSED**: Test completed successfully, configuration is correct
- **❌ FAILED**: Test failed, configuration issue detected
- **⏭️ SKIPPED**: Test skipped (feature not configured or not applicable)

### Common Failure Scenarios

1. **Feature Not Enabled**
   - Solution: Enable required features (`feature vn-segment-vlan-based`, `feature nv overlay`)

2. **NVE Interface Down**
   - Solution: Check source-interface configuration and underlay connectivity

3. **BGP EVPN Neighbors Down**
   - Solution: Verify BGP configuration, route reflector setup, and network connectivity

4. **Missing VNI Mappings**
   - Solution: Configure VNI-to-VLAN mappings and ensure consistency across fabric

5. **High Resource Usage**
   - Solution: Review VNI allocation and consider hardware capacity planning

## Logging and Debugging

### Log Levels
- **DEBUG**: Detailed execution information
- **INFO**: General test progress and results
- **WARNING**: Non-critical issues detected
- **ERROR**: Critical errors requiring attention

### Log Files
- Console output provides real-time test progress
- Detailed logs available in pyATS job logs directory
- HTML reports generated with `--html-logs` option

## Customization

### Adding Custom Tests

```python
class CustomVxlanTest(aetest.Testcase):
    """Custom VXLAN validation test"""
    
    @aetest.test
    def test_custom_validation(self, testbed):
        """Custom test implementation"""
        for device_name, device in testbed.devices.items():
            with aetest.steps.Step(f"Custom check on {device_name}") as step:
                # Your custom validation logic here
                pass
```

### Modifying Test Parameters

Edit the test thresholds and parameters in the code:

```python
# Example: Modify VNI usage warning threshold
if vni_count > 8000:  # Adjust threshold as needed
    step.failed(f"High VNI usage on {device_name}: {vni_count} VNIs")
```

## Troubleshooting

### Common Issues

1. **Connection Failures**
   ```
   Error: Failed to connect to device
   Solution: Verify IP addresses, credentials, and SSH connectivity
   ```

2. **Parser Errors**
   ```
   Error: Command output parsing failed
   Solution: Check NX-OS version compatibility and command syntax
   ```

3. **Permission Denied**
   ```
   Error: Insufficient privileges
   Solution: Ensure user has appropriate RBAC permissions
   ```

### Debug Mode

```bash
# Enable debug logging
python vxlan_validation.py --testbed testbed.yaml --loglevel DEBUG
```

## Best Practices

1. **Pre-Test Validation**
   - Verify basic device connectivity before running tests
   - Ensure VXLAN features are licensed and available

2. **Testbed Organization**
   - Group devices logically (leaf, spine, border-leaf)
   - Use consistent naming conventions

3. **Regular Testing**
   - Integrate into CI/CD pipelines for configuration validation
   - Run after configuration changes to detect issues early

4. **Monitoring Integration**
   - Export test results to monitoring systems
   - Set up alerts for critical test failures

## Support

For issues and questions:

1. Check the troubleshooting section above
2. Review pyATS documentation: https://pubhub.devnetcloud.com/media/pyats/docs/
3. Consult Cisco VXLAN configuration guides
4. Review device-specific documentation

## License

This test suite is provided as-is for educational and operational purposes. Ensure compliance with your organization's testing and validation policies.

---

**Note**: Always test in a non-production environment before deploying to production networks.