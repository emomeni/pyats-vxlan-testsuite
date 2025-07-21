# Enhanced VXLAN Validation Suite (Modular Version)

This repository provides a modular, production-grade validation framework for **Cisco Nexus VXLAN/EVPN fabrics** using **pyATS**, designed by a network automation engineer. It separates validation logic, parser utilities, and exception handling to allow **scalable**, **testable**, and **maintainable** fabric testing.

---

## 🧱 Repository Structure

| File/Module | Description |
|-------------|-------------|
| `enhanced_vxlan_testsuite.py` | Entry point for running the end-to-end validation suite |
| `base_test.py` | Abstract base class for building pyATS test cases |
| `vxlan_config.py` | Central configuration for CLI commands, thresholds, and features |
| `vxlan_utils.py` | Parser classes and utility functions (e.g., command output parsing, helpers) |
| `vxlan_validators.py` | Individual validators for platform, features, interfaces, VNIs, BGP EVPN |
| `vxlan_exceptions.py` | Custom exception definitions for standardized error handling |

---

## 🚀 Features

- 🔍 Modular validation for:
  - NX-OS version and hardware compatibility
  - Feature enablement (e.g., `nv overlay`, `vn-segment`)
  - Interface `nve1` configuration and state
  - NVE peer health
  - VNI-to-VLAN and VNI-to-VRF mappings
  - BGP EVPN neighbor state
  - Ingress replication check
  - Resource usage (VNI exhaustion risk)
- 📄 Structured validation results with:
  - `passed`, `message`, `details`, `recommendations`, `severity`
- 🧪 CI-friendly output for integration into GitLab/GitHub pipelines
- 🧰 Extensible for MPLS, LISP, or IP SLA validation

---

## 🛠️ Setup

### 1. Clone the Repository
```bash
git clone https://your.repo/pyats-vxlan-suite.git
cd pyats-vxlan-suite
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up pyATS Testbed
Create your `testbed.yaml` with the Nexus devices you want to validate.

### 4. Run the Suite
```bash
pyats run job enhanced_vxlan_testsuite.py --testbed-file testbed.yaml
```

---

## 🧪 Sample Output

Validation results are grouped into major components and structured like:
```json
{
  "component": "BGPValidator",
  "test": "validate_bgp_evpn",
  "result": {
    "passed": false,
    "message": "Only 2/3 BGP EVPN neighbors established",
    "severity": "error",
    "recommendations": ["Verify AS numbers", "Check routing to neighbors"]
  }
}
```

---

## 🤝 Contributing

- Add new validation logic in `vxlan_validators.py`
- Add parsing logic in `vxlan_utils.py`
- Extend config or thresholds via `vxlan_config.py`
- Use `ValidationResult` pattern for consistency

---

## 📚 References

- Cisco Nexus 9000 Series VXLAN EVPN Deployment Guide
- pyATS Documentation: https://developer.cisco.com/pyats/
- DevNet Code Exchange Best Practices

---

## 👨‍💻 Author

Developed by Ehsan – Network Automation Engineer with production experience in multi-vendor VXLAN fabrics, pyATS testing, and NetDevOps principles.

---

## 📄 License

MIT License (or specify if internal use only)
