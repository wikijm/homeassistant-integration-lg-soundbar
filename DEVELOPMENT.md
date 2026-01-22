# LG Soundbar Integration - Developer Documentation

## Protocol Implementation

This integration implements the proprietary LG soundbar network protocol based on the work from [pve84/lg_soundbar](https://github.com/pve84/lg_soundbar), which uses AES-encrypted TCP communication.

### Protocol Details

- **Transport**: TCP socket (default port 9741)
- **Encryption**: AES-256-CBC with fixed IV and key
- **Format**: JSON messages wrapped in encrypted packets
- **Packet Structure**: `[0x10][length:4 bytes big-endian][encrypted_payload]`

### Key Components

#### `temescal.py` - Communication Library

Handles all network communication with the soundbar:
- AES encryption/decryption with PKCS7 padding
- Async TCP socket connection
- Background listener for responses
- Message encoding/decoding

#### `media_player.py` - Entity Implementation

Home Assistant media player entity:
- State management (volume, mute, source, sound mode)
- Event handling from soundbar responses
- Command execution (volume, source, EQ changes)
- Periodic state polling

#### `config_flow.py` - Configuration UI

User interface for setup:
- Connection validation during setup
- IP address and port configuration
- Friendly name assignment

### Message Protocol

**Request Format:**
```json
{
  "cmd": "get" | "set",
  "msg": "MESSAGE_TYPE",
  "data": { /* optional payload */ }
}
```

**Response Format:**
```json
{
  "msg": "MESSAGE_TYPE",
  "data": { /* response data */ }
}
```

**Common Message Types:**
- `EQ_VIEW_INFO` - Equalizer/sound mode settings
- `SPK_LIST_VIEW_INFO` - Volume and speaker information  
- `FUNC_VIEW_INFO` - Input function/source information
- `SETTING_VIEW_INFO` - Advanced settings (woofer, rear speakers, etc.)
- `PRODUCT_INFO` - Device identification

### Supported Features

| Feature | Implementation |
|---------|----------------|
| Volume Control | `set_volume()`, `volume_up()`, `volume_down()` |
| Mute/Unmute | `set_mute(bool)` |
| Input Sources | `set_func(index)` with predefined functions list |
| Sound Modes | `set_eq(index)` with predefined equalisers list |
| State Polling | Periodic queries via `async_update()` |

### Input Sources (functions)

```python
["Wifi", "Bluetooth", "Portable", "Aux", "Optical", "CP", "HDMI",
 "ARC", "Spotify", "Optical2", "HDMI2", "HDMI3", "LG TV", "Mic",
 "Chromecast", "Optical/HDMI ARC", "LG Optical", "FM", "USB_old", "USB"]
```

### Sound Modes (equalisers)

```python
["Standard", "Bass", "Flat", "Boost", "Treble and Bass", "User",
 "Music", "Cinema", "Night", "News", "Voice", "ia_sound",
 "Adaptive Sound Control", "Movie", "Bass Blast", "Dolby Atmos",
 "DTS Virtual X", "Bass Boost Plus", "DTS:X"]
```

## Development Setup

### Local Testing

1. Create symbolic link to development directory:
```bash
ln -s /path/to/dev/lg_soundbar /config/custom_components/lg_soundbar
```

2. Enable debug logging in `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.lg_soundbar: debug
    custom_components.lg_soundbar.temescal: debug
```

3. Restart Home Assistant and monitor logs:
```bash
tail -f /config/home-assistant.log | grep lg_soundbar
```

### Network Debugging

Capture protocol traffic for analysis:
```bash
tcpdump -i any -s 0 -w lg_soundbar.pcap port 9741
```

### Testing Connection

```python
import asyncio
from custom_components.lg_soundbar.temescal import Temescal

async def test():
    device = Temescal("192.168.1.100", 9741)
    if await device.connect():
        await device.get_info()
        await asyncio.sleep(2)
        await device.disconnect()

asyncio.run(test())
```

## Adding New Features

### Example: Add Night Mode Control

1. **Add method to `temescal.py`:**
```python
async def set_night_mode(self, enable: bool):
    data = {
        "cmd": "set",
        "data": {"b_night_mode": enable},
        "msg": "SETTING_VIEW_INFO"
    }
    await self.send_packet(data)
```

2. **Handle response in `media_player.py`:**
```python
def _handle_event(self, response):
    if msg == "SETTING_VIEW_INFO":
        if "b_night_mode" in data:
            self._night_mode = data["b_night_mode"]
```

3. **Expose as entity attribute:**
```python
@property
def extra_state_attributes(self):
    attrs = {}
    if hasattr(self, '_night_mode'):
        attrs["night_mode"] = self._night_mode
    return attrs
```

## Common Issues

### Connection Failures
- Verify soundbar is powered on and network-connected
- Check firewall rules allow port 9741
- Confirm soundbar WiFi is enabled
- Try power cycling the soundbar

### Commands Not Working
- Enable debug logging to see responses
- Verify message format matches your model
- Some features are model-specific
- Check for error responses in logs

### Delayed Updates
- Polling interval is configurable in `const.py` 
- Responses may take 1-2 seconds
- Use callback handler for real-time updates

## Architecture Notes

### Async Design
All communication is fully asynchronous using `asyncio`:
- Non-blocking TCP connections
- Background listener thread
- Async command methods
- Proper cleanup on disconnect

### State Management
State is updated from soundbar responses:
- Callback handler processes incoming messages
- Internal state variables updated
- `schedule_update_ha_state()` triggers HA update
- Polling provides fallback if messages missed

### Error Handling
Multiple layers of error handling:
- Connection retry on send failures
- Timeout handling in config flow
- Graceful disconnect on errors
- Detailed logging for debugging

## References

- [Original Implementation](https://github.com/pve84/lg_soundbar) by pve84
- [Google Temescal](https://github.com/google/python-temescal) - Protocol library
- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [Media Player Entity](https://developers.home-assistant.io/docs/core/entity/media-player)
- [Config Flow Handler](https://developers.home-assistant.io/docs/config_entries_config_flow_handler)

## Contributing

Contributions welcome! Areas for improvement:
- Support for additional soundbar models
- Advanced feature implementation (rear speakers, woofer control)
- SSDP discovery support
- Configuration options UI
- Unit tests
- Documentation improvements

## License

MIT License - See LICENSE file for details

Based on original work:
- Copyright 2018 Google LLC (Temescal library)
- pve84's Home Assistant integration
