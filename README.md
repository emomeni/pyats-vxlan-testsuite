# 🔧 pyATS VXLAN Validation Test Suite

This repository is a comprehensive validation toolkit for **Cisco Nexus VXLAN/EVPN fabrics**, featuring:
- A modular production-grade test suite (`enhanced_*`)
- A lightweight self-contained script (`improved_*`)
- A hybrid implementation (`vxlan_validation.py`) following structured aetest modules

Designed for network automation engineers looking to scale fabric validations with **CI/CD compatibility**, **modular architecture**, and **deep visibility** into overlay health.

---

## 📁 Overview of Available Modes

| Type        | File/Entry Point                         | Best For                               | Modular | Reusable | CI/CD Ready |
|-------------|-------------------------------------------|-----------------------------------------|---------|----------|-------------|
| ✅ Modular  | `enhanced_vxlan_testsuite.py`             | Production-grade automation             | ✅      | ✅        | ✅           |
| ⚡ Lightweight | `improved_pyats_vxlan_testsuite.py`     | Quick lab tests / PoC / demos           | ❌      | ⚠️ Limited| ⚠️ Minimal    |
| 🧪 Structured Hybrid | `vxlan_validation.py` + `/tests/...` | Team use with reusable modules          | ✅      | ✅        | ✅           |

---

## ✅ 1. Modular VXLAN Suite (`enhanced_vxlan_testsuite.py`)

**Files:**
- `enhanced_vxlan_testsuite.py`: pyATS job file
- `base_test.py`: test scaffolding
- `vxlan_validators.py`: logic for each validation type
- `vxlan_utils.py`: output parsers & command helpers
- `vxlan_exceptions.py`: custom exception classes
- `vxlan_config.py`: constants, CLI patterns, thresholds

**Validations:**
- Platform compatibility, NX-OS versions
- Feature checks: `nv overlay`, `vn-segment`
- Interface/NVE1 operational status
- VNI-to-VLAN and VNI-to-VRF mappings
- Peer connectivity via `show nve peers`
- BGP EVPN session states
- Interface counter parsing and drop thresholds

Run with:
```bash
pyats run job enhanced_vxlan_testsuite.py --testbed-file testbed.yaml
```

---

## ⚡ 2. Lightweight Validator (`improved_pyats_vxlan_testsuite.py`)

**Key Traits:**
- All logic embedded in a single `.py` file
- Parses CLI output using inline regex
- Uses pyATS `aetest` for test execution
- No external dependencies — very portable

**Ideal For:**
- Small labs
- Temporary validation environments
- Demos, onboarding engineers to pyATS

Run with:
```bash
pyats run job improved_pyats_vxlan_testsuite.py --testbed-file testbed.yaml
```

---

## 🧪 3. Structured Hybrid Suite (`vxlan_validation.py`)

**Structure:**
- Entry: `vxlan_validation.py`
- Modules in `/tests/` directory:
  - `feature.py`, `interface.py`, `vni.py`, `bgp.py`, etc.

**Highlights:**
- Clearly separated test cases by domain
- Can be extended by adding new `aetest.Testcase` modules
- Compatible with Genie & pyATS-native reporting

**Command:**
```bash
python vxlan_validation.py --testbed testbed.yaml --loglevel INFO
```

---

## 🔧 Sample Testbed

```yaml
devices:
  leaf1:
    os: nxos
    platform: n9k
    connections:
      cli:
        protocol: ssh
        ip: 192.168.1.10
        port: 22
        username: admin
        password: password
```

---

## 🔍 Test Result Types

- ✅ **PASSED** – Config correct
- ❌ **FAILED** – Error detected
- ⏭ **SKIPPED** – Feature not enabled or test not applicable

---

## 🧠 Best Use Scenarios

| Use Case                     | Recommended Version              |
|------------------------------|----------------------------------|
| CI/CD Pipelines              | `enhanced_` or `vxlan_validation.py` |
| Ad hoc Troubleshooting       | `improved_`                      |
| Production Fabric Auditing   | `enhanced_`                      |
| Team Collaboration           | `vxlan_validation.py`            |
| Demo or Training             | `improved_`                      |

---

## 📚 Resources

- [pyATS Documentation](https://developer.cisco.com/pyats/)
- Cisco VXLAN Configuration Guide
- Nexus 9000 VXLAN EVPN Deployment Docs

---

## 👤 Author

**Ehsan** – Network Automation Engineer  
Experience in scalable fabric validation, CI-driven testing, and VXLAN production deployments

---

## 🪪 License

MIT License