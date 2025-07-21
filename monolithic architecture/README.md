# 🚀 Improved PyATS VXLAN Test Suite

This repository contains a **self-contained, production-grade test suite** for validating **VXLAN configuration and health** on **Cisco Nexus NX-OS switches** using Cisco's [pyATS](https://developer.cisco.com/pyats/) framework.

---

## 📌 Overview

This enhanced version (v2.0.0) is built for high-fidelity fabric validation using **a single-file script** — ideal for labs, PoCs, and quick CI/CD pipelines where **modularity isn't required**, but **robust parsing, validation, and exception handling are critical**.

---

## ✅ Features

- Full compatibility with Cisco Nexus 9000 platforms (NX-OS)
- Structured testcases for:
  - Platform and version compatibility
  - VXLAN/NVE feature enablement
  - NVE interface validation
  - VNI mapping and state checks
  - Peer and BGP neighbor health
  - Interface counters and error thresholds
- Robust parsing with `regex` and data classes
- Actionable error messages and guided remediation steps
- Safe CLI execution with `CommandExecutionError` and recommendations
- Built-in logger and `aetest` steps for structured reporting

---

## 🧪 Validations Performed

| Layer      | Scope                                                          |
|------------|----------------------------------------------------------------|
| Platform   | Checks for Nexus 9K/NX-OS and minimum supported version        |
| Feature    | Ensures `vn-segment-vlan-based` and `nv overlay` are enabled  |
| Interface  | Validates `nve1` status, source-interface, and line protocol  |
| Peers      | Checks `show nve peers` for reachability and state            |
| VNIs       | Parses and validates VNI types, VLANs, VRFs, and oper state   |
| Counters   | Parses `show interface nve1 counters` for errors/drops        |

---

## 📂 File: `improved_pyats_vxlan_testsuite.py`

This single script includes:
- Custom Exception classes
- Helper classes for parsing and execution
- All `aetest` testcases for modular VXLAN validation
- `argparse`-based CLI entrypoint
- Logging, structured steps, and metrics tracking

---

## 🧰 Usage

### Requirements

- Python 3.8+
- `pyATS` installed (`pip install pyats`)
- Valid testbed file (`YAML` format)

### Run the Script

```bash
pyats run job improved_pyats_vxlan_testsuite.py --testbed-file testbed.yaml
```

Optional flags:
- `--html-logs path/` to generate HTML reports
- `--loglevel DEBUG` for verbose output

---

## ⚙️ Example Configuration Snippet

```yaml
devices:
  leaf1:
    os: nxos
    type: switch
    connections:
      cli:
        protocol: ssh
        ip: 192.168.1.10
        port: 22
        username: admin
        password: password
```

---

## 📈 Output

- CLI-based logs (`INFO`, `WARN`, `ERROR`)
- Step-wise result summary from pyATS
- Optional: integrate with log systems (ELK, Splunk, etc.)

---

## 🧠 Why Use This?

✅ Better than ad hoc CLI checks  
✅ Safer than relying on fragile screen scraping  
✅ Ideal for automation pipelines and troubleshooting  
✅ A solid foundation for evolving into a modular framework later

---

## 📚 License

MIT

---

## 👨‍💻 Author

Ehsan — Network Automation Engineer