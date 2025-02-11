# Example reponse from initial 6-digit verification code
## Goal is to get the auth_token
```
{
	"id":3,
	"printer": {
		"id":2,
		"name":"My Awesome Cloud Printer",
		"created_at":"2025-02-10T21:49:02.834292Z",
		"action_on_failure":"PAUSE",
		"watching_enabled":true,
		"not_watching_reason":"Printer is not actively printing",
		"tools_off_on_pause":true,
		"bed_off_on_pause":false,
		"retract_on_pause":6.5,
		"lift_z_on_pause":2.5,
		"detective_sensitivity":1.0,
		"min_timelapse_secs_on_finish":600,
		"min_timelapse_secs_on_cancel":300,
		"auth_token":"fb9caf95f80ee41faca7",
		"archived_at":null,
		"agent_name":null,
		"agent_version":null,
		"pic":null,
		"status":null,
		"settings":
		{
			"webcam_flipV":false,
			"webcam_flipH":false,
			"webcam_rotate90":false,
			"webcam_rotation":0,
			"webcam_streamRatio":"16:9",
			"ratio169":true
		},
		"current_print":null,"normalized_p":0
	},
	"code":"122028",
	"expired_at":"2025-02-10T21:49:02.841816Z",
	"verified_at":"2025-02-10T21:49:02.841823Z"
}
```

# Possible API points - Tried Pulling from Obico-Octoprint

## verify_code
- Request: `POST /api/v1/octo/verify/?code=<code>`
- Parameters: `code, endpoint_prefix`
- Response Example:
	```
	{
	"succeeded": true,
	"printer": {
		"auth_token": "<auth_token>"
	}
	}
	```

## get_plugin_status
- Request: No external server request; returns the plugin's status.
- Response Example:
	```
	{
	"server_status": {
		"is_connected": true,
		"status_posted_to_server_ts": "<timestamp>",
		"bailed_because_tsd_plugin_running": false
	},
	"linked_printer": "<printer_info>",
	"streaming_status": {
		"webrtc_streaming": true
	},
	"error_stats": {...},
	"alerts": [...],
	"sentry_opt": "asked"
	}
	```

## toggle_sentry_opt
- Request: No external server request; toggles Sentry opt-in setting.
- Response: No specific response; action taken directly on plugin settings.

## test_server_connection
- Request: Tests server connection status.
- Response Example:
	```
	{
	"status_code": 200
	}
	```

## update_printer
- Request: `PATCH /api/v1/octo/printer/`
- Parameters: `name`
- Response Example:
	```
	{
	"succeeded": true,
	"printer": {
		"name": "<name>"
	}
	}
	```

## Device Information Collection and Unlinked Printer Registration:
- Endpoint: POST /api/v1/octo/unlinked/
- Request Data:
	```
	{
	"device_id": "<device_id>",
	"hostname": "<hostname>",
	"host_or_ip": "<host_or_ip>",
	"port": "<port>",
	"os": "<os>",
	"arch": "<arch>",
	"rpi_model": "<rpi_model>",
	"octopi_version": "<octopi_version>",
	"plugin_version": "<plugin_version>",
	"agent": "Obico for OctoPrint",
	"printerprofile": "<printer_profile>",
	"machine_type": "<machine_type>"
	}
	```
- Response Data:
	```
	{
	"messages": [
		{
		"type": "verify_code",
		"data": {
			"code": "<code>",
			"secret": "<device_secret>",
			"device_id": "<device_id>"
		}
		}
	]
	}
	```

## Code Verification:
- Endpoint: `POST /api/v1/octo/verify/?code=<code>`
- Request Data:
	```
	{
	"code": "<code>"
	}
	```
- Response Data:
	```
	{
	"succeeded": true,
	"printer": {
		"auth_token": "<auth_token>"
	}
	}
	```

## Version
# API Version
- Endpoint: `/v1/version/`
- Example Request: `GET /v1/version/`
- Example Response:
```
{
  "version": "1.0.0"
}
```

# API Endpoints pulled from Obico-Server (backend)

## Users
- Endpoint: `/v1/users/`
- Example Request: `GET /v1/users/`
- Example Response:
  ```json
  [
    {
      "id": 1,
      "username": "user1",
      "email": "user1@example.com"
    }
  ]
  ```

## Printers
- Endpoint: `/v1/printers/`
- Example Request: `GET /v1/printers/`
- Example Response:
  ```json
  [
    {
      "id": 1,
      "name": "Printer1",
      "status": "online"
    }
  ]
  ```

## Prints
- Endpoint: `/v1/prints/`
- Example Request: `GET /v1/prints/`
- Example Response:
  ```json
  [
    {
      "id": 1,
      "printer": 1,
      "status": "completed"
    }
  ]
  ```

## GCode Files
- Endpoint: `/v1/g_code_files/`
- Example Request: `GET /v1/g_code_files/`
- Example Response:
  ```json
  [
    {
      "id": 1,
      "filename": "file1.gcode",
      "printer": 1
    }
  ]
  ```

## GCode Folders
- Endpoint: `/v1/g_code_folders/`
- Example Request: `GET /v1/g_code_folders/`
- Example Response:
  ```json
  [
    {
      "id": 1,
      "name": "folder1",
      "printer": 1
    }
  ]
  ```

## Print Shot Feedbacks
- Endpoint: `/v1/printshotfeedbacks/`
- Example Request: `GET /v1/printshotfeedbacks/`
- Example Response:
  ```json
  [
    {
      "id": 1,
      "print": 1,
      "feedback": "Good"
    }
  ]
  ```

## OctoPrint Tunnel Usage
- Endpoint: `/v1/tunnelusage/`
- Example Request: `GET /v1/tunnelusage/`
- Example Response:
  ```json
  [
    {
      "id": 1,
      "tunnel": 1,
      "usage": 100
    }
  ]
  ```

## Mobile Devices
- Endpoint: `/v1/mobile_devices/`
- Example Request: `GET /v1/mobile_devices/`
- Example Response:
  ```json
  [
    {
      "id": 1,
      "device_id": "device1",
      "user": 1
    }
  ]
  ```

## One-Time Verification Codes
- Endpoint: `/v1/onetimeverificationcodes/`
- Example Request: `GET /v1/onetimeverificationcodes/`
- Example Response:
  ```json
  [
    {
      "id": 1,
      "code": "123456",
      "user": 1
    }
  ]
  ```

## Shared Resources
- Endpoint: `/v1/sharedresources/`
- Example Request: `GET /v1/sharedresources/`
- Example Response:
  ```json
  [
    {
      "id": 1,
      "resource": "resource1",
      "shared_with": 1
    }
  ]
  ```

## Printer Discovery
- Endpoint: `/v1/printer_discovery/`
- Example Request: `GET /v1/printer_discovery/`
- Example Response:
  ```json
  [
    {
      "id": 1,
      "printer": "printer1",
      "status": "discovered"
    }
  ]
  ```

## One-Time Passcodes
- Endpoint: `/v1/one_time_passcodes/`
- Example Request: `GET /v1/one_time_passcodes/`
- Example Response:
  ```json
  [
    {
      "id": 1,
      "passcode": "1234",
      "user": 1
    }
  ]
  ```

## OctoPrint Tunnels
- Endpoint: `/v1/tunnels/`
- Example Request: `GET /v1/tunnels/`
- Example Response:
  ```json
  [
    {
      "id": 1,
      "tunnel_id": "tunnel1",
      "printer": 1
    }
  ]
  ```

## Notification Settings
- Endpoint: `/v1/notification_settings/`
- Example Request: `GET /v1/notification_settings/`
- Example Response:
  ```json
  [
    {
      "id": 1,
      "user": 1,
      "settings": {
        "email": true,
        "sms": false
      }
    }
  ]
  ```

## Printer Events
- Endpoint: `/v1/printer_events/`
- Example Request: `GET /v1/printer_events/`
- Example Response:
  ```json
  [
    {
      "id": 1,
      "printer": 1,
      "event": "started"
    }
  ]
  ```

## First Layer Inspection Images
- Endpoint: `/v1/first_layer_inspection_images/`
- Example Request: `GET /v1/first_layer_inspection_images/`
- Example Response:
  ```json
  [
    {
      "id": 1,
      "image_url": "http://example.com/image1.jpg",
      "printer": 1
    }
  ]
  ```

## OctoPrint Pic
- Endpoint: `/v1/octo/pic/`
- Example Request: `GET /v1/octo/pic/`
- Example Response:
  ```json
  {
    "pic_url": "http://example.com/pic.jpg"
  }
  ```

## OctoPrint Ping
- Endpoint: `/v1/octo/ping/`
- Example Request: `GET /v1/octo/ping/`
- Example Response:
  ```json
  {
    "status": "pong"
  }
  ```

## OctoPrint Printer
- Endpoint: `/v1/octo/printer/`
- Example Request: `GET /v1/octo/printer/`
- Example Response:
  ```json
  {
    "printer_status": "online"
  }
  ```

## OctoPrint Unlinked
- Endpoint: `/v1/octo/unlinked/`
- Example Request: `GET /v1/octo/unlinked/`
- Example Response:
  ```json
  {
    "unlinked_printers": []
  }
  ```

## OctoPrint Verify
- Endpoint: `/v1/octo/verify/`
- Example Request: `POST /v1/octo/verify/`
  ```json
  {
    "code": "123456"
  }
  ```
- Example Response:
  ```json
  {
    "status": "verified"
  }
  ```

## OctoPrint Printer Events
- Endpoint: `/v1/octo/printer_events/`
- Example Request: `GET /v1/octo/printer_events/`
- Example Response:
  ```json
  [
    {
      "id": 1,
      "printer": 1,
      "event": "started"
    }
  ]
  ```

## Version
### API Version
- Endpoint: `/v1/version/`
- Example Request: `GET /v1/version/`
- Example Response:
  ```json
  {
    "version": "1.0.0"
  }
  ```

# Endpoints that accept POST requests:

## Printers
### Archive Printer
- Endpoint: `/v1/printers/{id}/archive/`
- Example Request: `POST /v1/printers/1/archive/`
- Example Response:
  ```
  Status: 204 No Content
  ```

### Cancel Print
- Endpoint: `/v1/printers/{id}/cancel_print/`
- Example Request: `POST /v1/printers/1/cancel_print/`
- Example Response:
  ```json
  {
    "succeeded": true,
    "printer": { ... }
  }
  ```

### Pause Print
- Endpoint: `/v1/printers/{id}/pause_print/`
- Example Request: `POST /v1/printers/1/pause_print/`
- Example Response:
  ```json
  {
    "succeeded": true,
    "printer": { ... }
  }
  ```

### Resume Print
- Endpoint: `/v1/printers/{id}/resume_print/`
- Example Request: `POST /v1/printers/1/resume_print/`
- Example Response:
  ```json
  {
    "succeeded": true,
    "printer": { ... }
  }
  ```

### Mute Current Print
- Endpoint: `/v1/printers/{id}/mute_current_print/`
- Example Request: `POST /v1/printers/1/mute_current_print/`
- Example Response:
  ```json
  {
    "succeeded": true,
    "printer": { ... }
  }
  ```

### Acknowledge Alert
- Endpoint: `/v1/printers/{id}/acknowledge_alert/`
- Example Request: `POST /v1/printers/1/acknowledge_alert/`
- Example Response:
  ```json
  {
    "succeeded": true,
    "printer": { ... }
  }
  ```

## Prints
### Bulk Delete
- Endpoint: `/v1/prints/bulk_delete/`
- Example Request: `POST /v1/prints/bulk_delete/`
  ```json
  {
    "print_ids": [1, 2, 3]
  }
  ```
- Example Response:
  ```
  Status: 204 No Content
  ```

## GCode Folders
### Bulk Delete
- Endpoint: `/v1/g_code_folders/bulk_delete/`
- Example Request: `POST /v1/g_code_folders/bulk_delete/`
  ```json
  {
    "folder_ids": [1, 2, 3]
  }
  ```
- Example Response:
  ```
  Status: 204 No Content
  ```

### Bulk Move
- Endpoint: `/v1/g_code_folders/bulk_move/`
- Example Request: `POST /v1/g_code_folders/bulk_move/`
  ```json
  {
    "folder_ids": [1, 2, 3],
    "parent_folder": 4
  }
  ```
- Example Response:
  ```
  Status: 204 No Content
  ```

## GCode Files
### Bulk Delete
- Endpoint: `/v1/g_code_files/bulk_delete/`
- Example Request: `POST /v1/g_code_files/bulk_delete/`
  ```json
  {
    "file_ids": [1, 2, 3]
  }
  ```
- Example Response:
  ```
  Status: 204 No Content
  ```

### Bulk Move
- Endpoint: `/v1/g_code_files/bulk_move/`
- Example Request: `POST /v1/g_code_files/bulk_move/`
  ```json
  {
    "file_ids": [1, 2, 3],
    "parent_folder": 4
  }
  ```
- Example Response:
  ```
  Status: 204 No Content
  ```

### Create GCode File
- Endpoint: `/v1/g_code_files/`
- Example Request: `POST /v1/g_code_files/`
  ```json
  {
    "filename": "file1.gcode",
    "parent_folder": 1
  }
  ```
- Example Response:
  ```json
  {
    "id": 1,
    "filename": "file1.gcode",
    "parent_folder": 1
  }
  ```

## OctoPrint Tunnel
### Create OctoPrint Tunnel
- Endpoint: `/v1/tunnels/`
- Example Request: `POST /v1/tunnels/`
  ```json
  {
    "target_printer_id": 1,
    "app_name": "AppName"
  }
  ```
- Example Response:
  ```json
  {
    "tunnel_endpoint": "http://example.com/tunnel"
  }
  ```

## Mobile Devices
### Register Mobile Device
- Endpoint: `/v1/mobile_devices/`
- Example Request: `POST /v1/mobile_devices/`
  ```json
  {
    "device_token": "token",
    "app_version": "1.0.0"
  }
  ```
- Example Response:
  ```json
  {
    "id": 1,
    "device_token": "token",
    "app_version": "1.0.0"
  }
  ```

## Shared Resources
### Create Shared Resource
- Endpoint: `/v1/sharedresources/`
- Example Request: `POST /v1/sharedresources/`
  ```json
  {
    "printer_id": 1
  }
  ```
- Example Response:
  ```json
  {
    "id": 1,
    "printer": 1,
    "share_token": "token"
  }
  ```

## One-Time Passcodes
### Verify One-Time Passcode
- Endpoint: `/v1/one_time_passcodes/`
- Example Request: `POST /v1/one_time_passcodes/`
  ```json
  {
    "verification_code": "123456",
    "one_time_passcode": "passcode"
  }
  ```
- Example Response:
  ```json
  {
    "detail": "OK"
  }
  ```

## Printer Discovery
### Verify Device Code
- Endpoint: `/v1/printer_discovery/`
- Example Request: `POST /v1/printer_discovery/`
  ```json
  {
    "code": "123456",
    "device_id": "device1",
    "device_secret": "secret"
  }
  ```
- Example Response:
  ```json
  {
    "queued": true
  }
  ```

## Notification Settings
### Send Test Message
- Endpoint: `/v1/notification_settings/{id}/send_test_message/`
- Example Request: `POST /v1/notification_settings/1/send_test_message/`
- Example Response:
  ```json
  {
    "status": "sent"
  }
  ```

# Endpoints that accept other Requets (PUT, DELETE, ETC.)

## GCode Files
### Create GCode File
- Endpoint: `/v1/g_code_files/`
- Request Type: POST
- Example Request:
  ```json
  {
    "filename": "file1.gcode",
    "parent_folder": 1
  }
  ```
- Example Response:
  ```json
  {
    "id": 1,
    "filename": "file1.gcode",
    "parent_folder": 1
  }
  ```

### Delete GCode File
- Endpoint: `/v1/g_code_files/{id}/`
- Request Type: DELETE
- Example Request: `DELETE /v1/g_code_files/1/`
- Example Response:
  ```
  Status: 204 No Content
  ```

## GCode Folders
### Bulk Delete
- Endpoint: `/v1/g_code_folders/bulk_delete/`
- Request Type: POST
- Example Request:
  ```json
  {
    "folder_ids": [1, 2, 3]
  }
  ```
- Example Response:
  ```
  Status: 204 No Content
  ```

## Prints
### Bulk Delete
- Endpoint: `/v1/prints/bulk_delete/`
- Request Type: POST
- Example Request:
  ```json
  {
    "print_ids": [1, 2, 3]
  }
  ```
- Example Response:
  ```
  Status: 204 No Content
  ```

## Printers
### Archive Printer
- Endpoint: `/v1/printers/{id}/archive/`
- Request Type: POST
- Example Request: `POST /v1/printers/1/archive/`
- Example Response:
  ```
  Status: 204 No Content
  ```

### Cancel Print
- Endpoint: `/v1/printers/{id}/cancel_print/`
- Request Type: POST
- Example Request: `POST /v1/printers/1/cancel_print/`
- Example Response:
  ```json
  {
    "succeeded": true,
    "printer": { ... }
  }
  ```

### Pause Print
- Endpoint: `/v1/printers/{id}/pause_print/`
- Request Type: POST
- Example Request: `POST /v1/printers/1/pause_print/`
- Example Response:
  ```json
  {
    "succeeded": true,
    "printer": { ... }
  }
  ```

### Resume Print
- Endpoint: `/v1/printers/{id}/resume_print/`
- Request Type: POST
- Example Request: `POST /v1/printers/1/resume_print/`
- Example Response:
  ```json
  {
    "succeeded": true,
    "printer": { ... }
  }
  ```

### Mute Current Print
- Endpoint: `/v1/printers/{id}/mute_current_print/`
- Request Type: POST
- Example Request: `POST /v1/printers/1/mute_current_print/`
- Example Response:
  ```json
  {
    "succeeded": true,
    "printer": { ... }
  }
  ```

### Acknowledge Alert
- Endpoint: `/v1/printers/{id}/acknowledge_alert/`
- Request Type: POST
- Example Request: `POST /v1/printers/1/acknowledge_alert/`
- Example Response:
  ```json
  {
    "succeeded": true,
    "printer": { ... }
  }
  ```

## OctoPrint Tunnel
### Create OctoPrint Tunnel
- Endpoint: `/v1/tunnels/`
- Request Type: POST
- Example Request:
  ```json
  {
    "target_printer_id": 1,
    "app_name": "AppName"
  }
  ```
- Example Response:
  ```json
  {
    "tunnel_endpoint": "http://example.com/tunnel"
  }
  ```

### Delete OctoPrint Tunnel
- Endpoint: `/v1/tunnels/{id}/`
- Request Type: DELETE
- Example Request: `DELETE /v1/tunnels/1/`
- Example Response:
  ```
  Status: 204 No Content
  ```

## Shared Resources
### Create Shared Resource
- Endpoint: `/v1/sharedresources/`
- Request Type: POST
- Example Request:
  ```json
  {
    "printer_id": 1
  }
  ```
- Example Response:
  ```json
  {
    "id": 1,
    "printer": 1,
    "share_token": "token"
  }
  ```

### Delete Shared Resource
- Endpoint: `/v1/sharedresources/{id}/`
- Request Type: DELETE
- Example Request: `DELETE /v1/sharedresources/1/`
- Example Response:
  ```
  Status: 204 No Content
  ```

## Mobile Devices
### Register Mobile Device
- Endpoint: `/v1/mobile_devices/`
- Request Type: POST
- Example Request:
  ```json
  {
    "device_token": "token",
    "app_version": "1.0.0"
  }
  ```
- Example Response:
  ```json
  {
    "id": 1,
    "device_token": "token",
    "app_version": "1.0.0"
  }
  ```

## One-Time Passcodes
### Verify One-Time Passcode
- Endpoint: `/v1/one_time_passcodes/`
- Request Type: POST
- Example Request:
  ```json
  {
    "verification_code": "123456",
    "one_time_passcode": "passcode"
  }
  ```
- Example Response:
  ```json
  {
    "detail": "OK"
  }
  ```

## Printer Discovery
### Verify Device Code
- Endpoint: `/v1/printer_discovery/`
- Request Type: POST
- Example Request:
  ```json
  {
    "code": "123456",
    "device_id": "device1",
    "device_secret": "secret"
  }
  ```
- Example Response:
  ```json
  {
    "queued": true
  }
  ```

## Notification Settings
### Send Test Message
- Endpoint: `/v1/notification_settings/{id}/send_test_message/`
- Request Type: POST
- Example Request: `POST /v1/notification_settings/1/send_test_message/`
- Example Response:
  ```json
  {
    "status": "sent"
  }
  ```

# Endpoints to Focus on re Initial Setup (need to test these):

## Code Verification
- Request: `POST /api/v1/octo/verify/?code=<code>` or possibly `GET /api/v1/octo/verify/?code=<code>`

## OctoPrint Printer
- Request: `PATCH /api/v1/octo/printer/` or `GET /v1/octo/printer/`

## One-Time Verification Codes
- Request: `GET /v1/onetimeverificationcodes/`

## Shared Resources
- Request: `GET /v1/sharedresources/`

## Printer Discovery
- Request: `GET /v1/printer_discovery/` or `POST /v1/printer_discovery/`

## One-Time Passcodes
- Example Request: `GET /v1/one_time_passcodes/` or `POST /v1/one_time_passcodes/`

## OctoPrint Ping
- Example Request: `GET /v1/octo/ping/`

## Acknowledge Alert
- Request: `/v1/printers/{id}/acknowledge_alert/` -- Example: `POST /v1/printers/1/acknowledge_alert/`
