# LG Soundbar Home Assistant Integration

## Project Summary

A fully functional Home Assistant custom integration for controlling LG soundbars over the network using the proprietary LG protocol (based on the reference implementation from pve84/lg_soundbar).

## What's Implemented

### ✅ Complete Features

1. **Network Communication (temescal.py)**
   - AES-256-CBC encrypted TCP socket communication
   - Async/await pattern throughout
   - Background listener for real-time updates
   - Connection management and error handling

2. **Media Player Entity (media_player.py)**
   - Volume control (set, up, down, mute)
   - Input source selection (HDMI, Optical, Bluetooth, etc.)
   - Sound mode selection (Standard, Cinema, Music, etc.)
   - Real-time state updates via callbacks
   - Periodic polling for state synchronization

3. **UI Configuration (config_flow.py)**
   - User-friendly setup through Home Assistant UI
   - Connection validation during setup
   - Unique device identification
   - Error handling and user feedback

4. **Integration Structure**
   - Proper manifest.json with dependencies
   - Localization support (strings.json)
   - Device information registry
   - Entry setup and cleanup

## File Structure

```
homeassistant-lg-soundbar/
├── custom_components/
│   └── lg_soundbar/
│       ├── __init__.py              # Integration setup
│       ├── config_flow.py           # UI configuration
│       ├── const.py                 # Constants
│       ├── manifest.json            # Metadata + dependencies
│       ├── media_player.py          # Media player entity
│       ├── temescal.py              # Protocol implementation
│       ├── strings.json             # UI strings
│       └── translations/
│           └── en.json              # English translations
├── .gitignore                       # Git ignore rules
├── .vscode/                         # VS Code settings
├── configuration.yaml.example       # Example config
├── DEVELOPMENT.md                   # Developer documentation
├── hacs.json                        # HACS metadata
├── LICENSE                          # MIT License
└── README.md                        # User documentation

```

## Key Capabilities

### Protocol Implementation
- Port: 9741 (default)
- Transport: TCP with AES encryption
- Message format: Encrypted JSON packets
- Bidirectional communication

### Supported Commands
- **Volume**: Set level (0-100), mute/unmute, step up/down
- **Sources**: 20 input types (HDMI, Optical, Bluetooth, WiFi, etc.)
- **Sound Modes**: 19 EQ presets (Standard, Cinema, Dolby Atmos, etc.)
- **State Query**: Real-time state monitoring
- **Advanced**: Bass, treble, woofer control (model dependent)

### Home Assistant Integration
- Media player entity type
- Device registry integration
- Config flow (UI setup)
- State attributes
- Service calls
- Event-driven updates

## Installation Methods

1. **HACS** (Recommended)
   - Add as custom repository
   - Install with one click
   - Automatic updates

2. **Manual**
   - Copy custom_components folder
   - Restart Home Assistant
   - Configure via UI

## Configuration

Simple 3-step setup:
1. Add Integration → Search "LG Soundbar"
2. Enter IP address and port (9741)
3. Assign friendly name

## Usage Examples

### Basic Control
```yaml
# Set volume to 50%
service: media_player.volume_set
target:
  entity_id: media_player.lg_soundbar
data:
  volume_level: 0.5

# Switch to HDMI input
service: media_player.select_source
target:
  entity_id: media_player.lg_soundbar
data:
  source: "HDMI"

# Enable Cinema mode
service: media_player.select_sound_mode
target:
  entity_id: media_player.lg_soundbar
data:
  sound_mode: "Cinema"
```

### Automation Example
```yaml
# Sync soundbar with TV
automation:
  - alias: "TV and Soundbar Sync"
    trigger:
      - platform: state
        entity_id: media_player.tv
        to: "playing"
    action:
      - service: media_player.select_source
        target:
          entity_id: media_player.lg_soundbar
        data:
          source: "HDMI"
      - service: media_player.volume_set
        target:
          entity_id: media_player.lg_soundbar
        data:
          volume_level: 0.4
```

## Requirements

- **Home Assistant**: 2024.1.0 or newer
- **Python**: 3.11+ (comes with HA)
- **Dependencies**: pycryptodome==3.20.0 (auto-installed)
- **Network**: LG soundbar must be on same network
- **Hardware**: WiFi-enabled LG soundbar

## Compatible Models

Tested with LG soundbars that support network control:
- LG SN series (SN11RG, SN10YG, SN9YG, etc.)
- LG SL series
- LG SK series
- Other WiFi-enabled models

## Technical Details

### Protocol Specifications
- **Encryption**: AES-256-CBC with fixed key/IV
- **Packet Header**: 0x10 + 4-byte length (big-endian)
- **Payload**: PKCS7-padded JSON messages
- **Port**: 9741 (TCP)

### Message Types
- `EQ_VIEW_INFO` - Equalizer settings
- `SPK_LIST_VIEW_INFO` - Speaker/volume info
- `FUNC_VIEW_INFO` - Input function info
- `SETTING_VIEW_INFO` - Advanced settings
- `PRODUCT_INFO` - Device information

## Documentation

- **README.md**: User installation and usage guide
- **DEVELOPMENT.md**: Developer documentation and protocol details
- **configuration.yaml.example**: Example automations
- **Code comments**: Inline documentation throughout

## License

MIT License - Free to use, modify, and distribute

## Credits

Based on:
- [pve84/lg_soundbar](https://github.com/pve84/lg_soundbar) - Original HA integration
- [Google Temescal](https://github.com/google/python-temescal) - Protocol library

## Status

✅ **Production Ready** - Fully functional integration with:
- Complete protocol implementation
- Proper error handling
- Connection validation
- Real-time state updates
- Comprehensive documentation
- Example configurations

Ready for:
- Installation via HACS
- Direct use by end users
- Community contributions
- Model-specific enhancements
