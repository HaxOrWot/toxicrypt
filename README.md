# TOXICRYPT - A Cryptographic Threat Emulation & Key Management Tool

[![Security Research](https://img.shields.io/badge/Focus-Ethical%20Hacking%20%26%20Research-blue.svg)](https://github.com/)
[![Python 3.x](https://img.shields.io/badge/Python-3.x-brightgreen.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 1. Project Overview & Research Objectives

This repository contains a proof-of-concept **Distributed Cryptographic Threat Emulation Framework**. Built for cybersecurity researchers, malware analysts, and red team operators, this project simulates the full operational lifecycle of hybrid ransomware strains in a controlled environment. 

The primary goal of this research tool is to analyze:
* **Hybrid Cryptographic Workflows:** How symmetric and asymmetric ciphers interact during real-time data lockup and recovery.
* **Command & Control (C2) Key Exchange:** Mechanics of out-of-band key exfiltration to a remote server.
* **Detection & Mitigation Strategies:** How endpoint detection (EDR) solutions and behavioral analytics monitor recursive directory traversal and rapid key exchange patterns.

---

## 2. Technical Stack

* **Language:** Python 3.x
* **Cryptographic Primitives:** PyCryptodome (`AES-256-CBC/GCM`, `RSA-2048/4096`)
* **Transport / Networking:** HTTP/S REST API via `Requests` & `Flask` / `FastAPI`
* **Backend Database:** SQLite / PostgreSQL (Key mapping and lifecycle tracking)

---

## 3. Threat Model & Architectural Overview

The system models a multi-component distributed threat architecture comprising a client payload, a recovery tool, a key-orchestration server (C2), and an administrative control panel.

```
+-------------------+        1. Transmit Encrypted AES Key       +--------------------+
|   Client Payload  | -----------------------------------------> |   Key Orchestrator |
|  (Enc Module)     |                                            |    (Server / DB)   |
+-------------------+                                            +--------------------+
          |                                                                ^
          | 2. File Traversal & Encryption                                 | 3. Authorize State
          v                                                                |
+-------------------+        4. Deliver RSA Private Key          +--------------------+
|   Recovery Tool   | <----------------------------------------- | Admin Console      |
|  (Dec Module)     |                                            | (Control Interface)|
+-------------------+                                            +--------------------+
```

### Modular Breakdown

#### A. The Encryption Engine (Payload Node)
* **Hybrid Cryptography:** Utilizes high-speed **AES-256** for bulk file payload processing. The session key is encapsulated using a public **RSA** key before transport.
* **Targeted Directory Traversal:** Implements recursive file-system walking tuned to specific high-value data extensions while preserving OS stability.
* **C2 Telemetry & Exfiltration:** Transmits encrypted session tokens and unique host hardware identifiers (HWID) over structured HTTP/S REST calls.

#### B. The Decryption Engine (Recovery Module)
* **Identity Verification:** Queries the central server using the host hardware ID to request recovery material.
* **Asymmetric Session Decryption:** Applies the server-issued private RSA key to unwrap the AES session key.
* **Data Restoration:** Reverses file transformation across target directories in-place to confirm total data integrity post-analysis.

#### C. Central Key Orchestration Server (C2 Backend)
* **Cryptographic Vault:** Maintains relational mappings of Host IDs, encrypted session keys, and state progression (`Pending` vs `Authorized`).
* **REST API Endpoints:** Handles incoming payload registration requests and handles authorized key release.

#### D. Administrative Control Console (Operator Interface)
* **Session Lifecycle Management:** Allows security operators to inspect connected endpoints, query pending sessions, and simulate authorization workflows.
* **Key Release Triggering:** Releases stored RSA key pairs to legitimate recovery tools upon state change.

---

## 4. Installation & Setup

Set up the framework in an isolated lab environment:

```bash
# Clone the repository
git clone https://github.com/HaxOrWot/toxicrypt.git
cd toxicrypt

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# FOR Server just start the server
python server.py
```
> **NOTE:** If you are facing issue while trying to modifying the status, You can just use the `admin_tool.py` to do so just run `python admin_tool.py <id>`

---

## 5. Lab Execution & Defensive Research

To execute security tests and observe telemetry safely:

1. **Host Environment:** Always run the payload in an isolated **Virtual Machine (VM)** or isolated malware analysis sandbox.
2. **Directory Isolation:** Configure the client configuration file to point strictly to a dedicated dummy directory (e.g., `./sandbox_target/`).
3. **Behavioral Analysis Workflow:**
   * Launch `server.py` and start network capture tools (e.g., Wireshark, Process Monitor).
   * Run the payload on dummy files to analyze file I/O speed, extension mutation, and API request signatures.
   * Use `admin.py` to transition the session state from `Pending` to `Authorized`.
   * Run the recovery tool to demonstrate key recovery and file restoration.

---

## 6. Defensive Countermeasures & Indicators of Compromise (IoCs)

When researching this framework, security teams can develop signatures around:
* **High-Volume File Modification:** Sudden surges in entropy and file write operations across user directories.
* **Unusual API Connections:** Outbound HTTP/S requests carrying structured JSON payloads with machine identifiers.
* **Cryptographic Key Artifacts:** Memory artifacts matching temporary AES key allocations prior to process termination.

---

## 7. Security Disclaimer

> ⚠️ **RESEARCH USE ONLY:** This repository is published strictly for educational, defensive research, and authorized red team simulation purposes. Unauthorized deployment against systems without explicit, written permission from the owner is illegal and strictly prohibited. The author assumes no liability for misuse or damage caused by this software.
