# pyATS VXLAN Test Suite

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
- Python 3.6 or higher
- pyATS framework
- Genie library

Install core dependencies:
```bash
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
   # Clone the repository
   git clone https://github.com/emomeni/pyats-vxlan-testsuite.git
   cd pyats-vxlan-testsuite
   
   # Or download directly
   wget https://github.com/emomeni/pyats-vxlan-testsuite/archive/main.zip
   unzip main.zip
   ```

2. **Install dependencies:**
   ```bash
   pip install pyats[full] genie
   ```

3. **Make the script executable:**
   ```bash
   chmod +x vxlan_validation.py
   ```

## Configuration

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

### Basic Usage
```bash
python vxlan_validation.py --testbed testbed.yaml
```

### Advanced Options
```bash
# Run with specific log level
python vxlan_validation.py --testbed testbed.yaml --loglevel INFO

# Run specific test classes only
python vxlan_validation.py --testbed testbed.yaml --testcase VxlanFeatureValidation

# Generate detailed HTML report
python vxlan_validation.py --testbed testbed.yaml --html-logs ./reports/
```

## Test Categories

### 1. Feature Validation
- **VXLAN Feature Status**: Verifies `feature vn-segment-vlan-based` is enabled
- **NVE Feature Status**: Confirms `feature nv overlay` is enabled

### 2. NVE Interface Tests
- **NVE Interface Status**: Checks NVE1 interface operational state
- **Source Interface**: Validates source-interface configuration
- **Peer Relationships**: Verifies NVE peer connectivity and status

### 3. VNI Configuration Tests
- **VNI-to-VLAN Mapping**: Confirms proper Layer 2 VNI associations
- **Ingress Replication**: Validates replication methods (BGP/Static)
- **VNI Configuration**: Checks VNI operational parameters
- **L3 VNI Configuration**: Verifies L3 VNI and VRF associations

### 4. Layer 3 Gateway Tests
- **Anycast Gateway**: Validates anycast gateway MAC configuration
- **SVI Interfaces**: Checks SVI interface configurations

### 5. BGP EVPN Tests
- **BGP EVPN Configuration**: Verifies BGP L2VPN EVPN address family
- **Neighbor Relationships**: Checks BGP EVPN neighbor states
- **Route Advertisement**: Validates EVPN route advertisements and RDs

### 6. MAC Address Learning
- **MAC Address Tables**: Verifies MAC learning in VXLAN VLANs
- **Remote MAC Entries**: Checks remote MAC address learning

### 7. Multicast Tests
- **Multicast Groups**: Validates multicast group configurations (if used)
- **Multicast Forwarding**: Checks multicast forwarding for BUM traffic

### 8. Performance & Monitoring
- **Interface Statistics**: Monitors NVE interface counters for errors
- **Resource Usage**: Tracks VNI utilization and capacity planning
- **Performance Metrics**: Identifies potential performance issues

## Test Results

### Status Indicators
- ✅ **PASSED**: Test completed successfully, configuration is correct
- ❌ **FAILED**: Test failed, configuration issue detected
- ⏭️ **SKIPPED**: Test skipped (feature not configured or not applicable)

### Common Issues and Solutions

#### Feature Not Enabled
- **Solution**: Enable required features (`feature vn-segment-vlan-based`, `feature nv overlay`)

#### NVE Interface Down
- **Solution**: Check source-interface configuration and underlay connectivity

#### BGP EVPN Neighbors Down
- **Solution**: Verify BGP configuration, route reflector setup, and network connectivity

#### Missing VNI Mappings
- **Solution**: Configure VNI-to-VLAN mappings and ensure consistency across fabric

#### High Resource Usage
- **Solution**: Review VNI allocation and consider hardware capacity planning

## Logging

### Log Levels
- **DEBUG**: Detailed execution information
- **INFO**: General test progress and results
- **WARNING**: Non-critical issues detected
- **ERROR**: Critical errors requiring attention

### Output Options
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

### Modifying Thresholds
Edit the test thresholds and parameters in the code:
```python
# Example: Modify VNI usage warning threshold
if vni_count > 8000:  # Adjust threshold as needed
    step.failed(f"High VNI usage on {device_name}: {vni_count} VNIs")
```

## Troubleshooting

### Connection Failures
- **Error**: Failed to connect to device
- **Solution**: Verify IP addresses, credentials, and SSH connectivity

### Parser Errors
- **Error**: Command output parsing failed
- **Solution**: Check NX-OS version compatibility and command syntax

### Permission Denied
- **Error**: Insufficient privileges
- **Solution**: Ensure user has appropriate RBAC permissions

### Debug Mode
Enable debug logging for detailed troubleshooting:
```bash
python vxlan_validation.py --testbed testbed.yaml --loglevel DEBUG
```

## Best Practices

### Pre-Test Validation
- Verify basic device connectivity before running tests
- Ensure VXLAN features are licensed and available

### Testbed Organization
- Group devices logically (leaf, spine, border-leaf)
- Use consistent naming conventions

### Regular Testing
- Integrate into CI/CD pipelines for configuration validation
- Run after configuration changes to detect issues early

### Monitoring Integration
- Export test results to monitoring systems
- Set up alerts for critical test failures

## Support

For issues and questions:
- Check the troubleshooting section above
- Review pyATS documentation: [https://pubhub.devnetcloud.com/media/pyats/docs/](https://pubhub.devnetcloud.com/media/pyats/docs/)
- Consult Cisco VXLAN configuration guides
- Review device-specific documentation

## License

This test suite is provided as-is for educational and operational purposes. Ensure compliance with your organization's testing and validation policies.

## Disclaimer

**Note**: Always test in a non-production environment before deploying to production networks.

---

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests to improve this test suite.
