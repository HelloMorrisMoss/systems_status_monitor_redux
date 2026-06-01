# Disk Check

The `disk` check monitors free space on a specific logical drive of a remote Windows host using WMIC.

## Description

This check parses the output of WMIC to determine the free space and total size of a disk drive (e.g., `C:`). It compares the free space against configured warning and critical thresholds.

## Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `drive` | string | `"C:"` | The drive letter to monitor (case-insensitive). |
| `warning_gb` | number | `10` | Free space threshold in GB for a **WARNING** status. |
| `critical_gb` | number | `5` | Free space threshold in GB for a **CRITICAL** status. |

## Example Configuration

```json
{
  "id": "example-system",
  "name": "Example Server",
  "address": "192.168.1.10",
  "username": "monitor-user",
  "password": "example-password",
  "checks": [
    {
      "id": "c-drive-space",
      "name": "C: Drive",
      "type": "disk",
      "params": {
        "drive": "C:",
        "warning_gb": 20,
        "critical_gb": 10
      }
    }
  ]
}
```

## Logic

1. The monitor connects via SSH and executes: `wmic logicaldisk get Caption,FreeSpace,Size`.
2. It parses the output table to find the row where `Caption` matches the configured `drive`.
3. It extracts `FreeSpace` and `Size` (provided by Windows in bytes).
4. It converts the values to Gigabytes (GB).
5. Evaluation:
   - If `free_gb <= critical_gb` -> **CRITICAL**
   - Else if `free_gb <= warning_gb` -> **WARNING**
   - Otherwise -> **OK**
6. If the drive is not found or the command fails, the status is marked accordingly (**UNKNOWN** or **CRITICAL**).
