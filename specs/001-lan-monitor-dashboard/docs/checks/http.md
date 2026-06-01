# HTTP Check

The `http` check performs an HTTP GET request to a specified URL and validates the response status code and body content.

## Description

Unlike other checks that run over SSH, the HTTP check is performed directly by the monitor server. It is ideal for checking the availability of web applications or internal APIs.

## Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | string | (Required) | The full URL to request (e.g., `http://192.168.1.10:8080/health`). |
| `status_code` | number | `200` | The expected HTTP response status code. |

### Rules

Optional `rules` can be defined to validate the response body.

| Property | Type | Options | Description |
|----------|------|---------|-------------|
| `type` | string | `contains`, `not_contains`, `regex` | The type of match to perform. |
| `pattern` | string | N/A | The string or regular expression to look for in the response body. |

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
      "id": "web-health",
      "name": "Web Application Health",
      "type": "http",
      "params": {
        "url": "http://192.168.1.10:8080/health",
        "status_code": 200
      },
      "rules": [
        {
          "type": "contains",
          "pattern": "UP"
        }
      ]
    }
  ]
}
```

## Logic

1. The monitor server sends an HTTP GET request to the configured `url`.
2. **Connection Check**: If the connection fails (e.g., DNS error, connection refused, or timeout), the check is marked as **CRITICAL**.
3. **Status Code Check**: The received HTTP status code is compared against the `expected_status_code` (default 200). If they do not match, the check is marked as **CRITICAL**.
4. **Rule Evaluation**: If the status code matches, any defined rules are evaluated against the response body content.
5. **Status Determination**:
   - If ALL rules pass -> **OK**.
   - If ANY rule fails -> **CRITICAL**.
6. The dashboard displays the result summary and a snippet of the response body for debugging.
