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

# Possible API points

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
