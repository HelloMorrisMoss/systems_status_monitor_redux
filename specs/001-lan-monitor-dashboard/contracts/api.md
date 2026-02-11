# API Contracts

## Status Endpoint
`GET /api/status`

Returns the current status of all monitored systems.

### Response `200 OK`
```json
{
  "systems": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Legacy-Server-1",
      "address": "192.168.1.10",
      "status": "OK",
      "last_checked": "2026-02-11T13:00:00Z",
      "checks": [
        {
          "name": "Time Check",
          "status": "OK",
          "summary": "13:00:05"
        },
        {
          "name": "Disk C:",
          "status": "OK",
          "summary": "45GB free / 100GB total"
        }
      ]
    }
  ],
  "global_status": "OK",
  "refreshing": false
}
```

## Refresh Endpoint
`POST /api/refresh`

Triggers an immediate update of all systems.

### Response `202 Accepted`
```json
{
  "message": "Refresh initiated"
}
```

## Health Endpoint
`GET /health`

### Response `200 OK`
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```
