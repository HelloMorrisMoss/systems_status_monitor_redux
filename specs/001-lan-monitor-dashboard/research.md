# Phase 0: Research - SSH-based Monitoring for Windows

## Overview
Monitoring Windows systems via SSH requires handling differences in shell environments (CMD vs PowerShell) and command availability (especially on legacy systems).

## SSH for Windows
- **OpenSSH on Windows**: Standard on modern Windows 10/11 and Server 2019+.
- **Authentication**: Initial support for password auth, future-proofing for SSH keys.
- **Library**: `paramiko` is the standard Python library for SSH. It is robust and supports password/key auth.

## Command Strategy
To support legacy Windows, we should prioritize commands that have existed for a long time.

### 1. System Time
- **Command**: `time /T` (CMD) or `Get-Date` (PowerShell).
- **Fallback**: `echo %DATE% %TIME%`.

### 2. Disk Free Space
- **Command**: `wmic logicaldisk get caption,freespace,size` (Legacy friendly, WMIC is available).
- **PowerShell**: `Get-PSDrive -PSProvider FileSystem`.
- **Note**: WMIC is being deprecated but is the most reliable for "legacy" Windows as requested.

### 3. Service Status
- **Command**: `sc query [ServiceName]` (Standard Windows Service Controller).
- **Fallback**: `tasklist` to check for running processes.

## Connectivity & Security
- **Timeouts**: Paramiko supports connection timeouts.
- **Error Handling**: Differentiate between "Connection Failed" (Network), "Auth Failed" (Credentials), and "Command Failed" (System-specific).

## Research Outcomes
1. Use `paramiko` for SSH communication.
2. Use `wmic` as the primary data source for disk info due to legacy requirements.
3. Implement a "Shell Detection" step or use fixed CMD-compatible commands.
