# Custom Command Check

The `custom` check allows running any shell command on the remote Windows host and validating its output against specific rules.

## Description

This is the most flexible check type. It executes a command via SSH and evaluates the results based on the exit code and optional string-matching rules.

## Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `command` | string | (Required) | The shell command to execute on the remote host. |

### Rules

You can define a list of `rules` to evaluate the command's standard output (`stdout`).

| Property | Type | Options | Description |
|----------|------|---------|-------------|
| `type` | string | `contains`, `not_contains`, `regex` | The type of match to perform. |
| `pattern` | string | N/A | The string or regular expression to look for. |

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
      "id": "service-status",
      "name": "My Application Service",
      "type": "custom",
      "command": "sc query MyAppService",
      "rules": [
        {
          "type": "contains",
          "pattern": "RUNNING"
        }
      ]
    }
  ]
}
```

## Logic

1. The monitor executes the `command` on the remote host via SSH.
2. **Exit Code Check**: If the command returns a non-zero exit code, the check immediately fails with **CRITICAL** status.
3. **Rule Evaluation**: If the exit code is 0, the monitor evaluates each defined rule against the `stdout`.
4. **Status Determination**:
   - If ALL rules pass -> **OK**.
   - If ANY rule fails -> **CRITICAL**.
5. The dashboard displays the first failed rule or a success message, along with a truncated version of the command output for debugging.
