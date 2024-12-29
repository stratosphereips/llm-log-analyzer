# LLM Log Analyzer

A simple python program to read a text file (designed for log files), and a prompt, and ask a local ollama server to analyze it.

## Features

- Contact local ollama

## Install

```bash
python -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

You also need ollama running in localhost.

## Usage

`python ./log-analyzer.py -f test-auth.log -c prompt.yaml`

# Example output
```bash
python ./log-analyzer.py -f test-auth.log -c prompt.yaml

============================================================
LLM RESPONSE:
============================================================
Based on the syslog lines, suspicious and abnormal behavior is observed:

1. Repeated occurrences of deprecated options "RSAAuthentication" and "RhostsRSAAuthentication" being reprocessed. This could indicate that the system's SSH configuration is not up-to-date or is being overwritten by an automated process.

2. Successful login attempts for users 'project' and 'root' from unknown IP addresses (147.12.82.196, 221.10.11.111). The authenticity of these logins cannot be verified due to the deprecated authentication methods used.

3. A successful public key authentication attempt for user 'dev' from a trusted IP address (8.8.8.8) using RSA SHA256 encryption. This is an acceptable behavior, as it indicates secure access via public key authentication.

However, malicious activity could also be inferred in the following lines:

1. An anonymous connection closed by an unknown IP address (192.168.42.20). The reason for this closure is unclear.

2. A failed password attempt from a different unknown IP address (221.10.11.111) and another known IP address that was expected to be authenticated successfully ('root' of 8.8.8.8), with the log noting "preauth" after the connection closure, possibly hinting at an external authentication mechanism like Kerberos or RDP.
============================================================

```

# About

This tool was developed at the Stratosphere Laboratory at the Czech Technical University in Prague.
