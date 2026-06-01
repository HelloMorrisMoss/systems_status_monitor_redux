# Time Check

The `time` check retrieves the current system time from a remote Windows host. This is useful for verifying that the system is responsive and that its clock is synchronized.

## Description

The check executes a command on the remote system to retrieve the time. It is a simple "up/down" check that also provides the current time in the dashboard summary.

## Configuration Parameters

This check type does not require any additional parameters.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| N/A       | N/A  | N/A     | No parameters required for this check. |

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
      "id": "system-time",
      "name": "Current Time",
      "type": "time"
    }
  ]
}
```

## Logic

1. The monitor connects to the remote system via SSH.
2. It attempts to execute `time /T` or a similar command to get the system time.
3. If the command succeeds (exit code 0), the check is marked as **OK**.
4. The output (the time) is displayed in the check summary.
5. If the command fails or returns no output, the check is marked as **CRITICAL** or **UNKNOWN**.
