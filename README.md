# Home Assistant LG Soundbar Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

A custom Home Assistant integration for controlling LG Soundbars over the network using the proprietary LG protocol.

## Features

- 🔊 **Volume Control** - Set volume level, increase/decrease, mute/unmute
- 🎵 **Sound Modes** - Select between Standard, Bass, Cinema, Music, and more
- 🔌 **Input Sources** - Switch between HDMI, Optical, Bluetooth, WiFi, and other inputs
- 🎛️ **Advanced Settings** - Control bass, treble, woofer levels (model dependent)
- 🏠 **Full Home Assistant Integration** - Media player entity with complete UI support
- 🎨 **UI Configuration** - Easy setup through Home Assistant's UI (no YAML needed)

## Compatibility

This integration works with LG soundbars that support the proprietary LG network protocol (typically port 9741). This includes many WiFi-enabled LG soundbar models such as:

- LG SN series (SN11RG, SN10YG, SN9YG, etc.)
- LG SL series
- LG SK series
- Other WiFi-enabled LG soundbars

**Note:** Your soundbar must be connected to your network via WiFi or Ethernet for this integration to work.

## Installation

### HACS (Recommended)

1. Make sure you have [HACS](https://hacs.xyz/) installed
2. Add this repository as a custom repository in HACS:
   - Go to HACS → Integrations
   - Click the three dots menu → Custom repositories
   - Add the repository URL: `https://github.com/yourusername/homeassistant-lg-soundbar`
   - Select "Integration" as the category
3. Click "Install" on the LG Soundbar integration
4. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/lg_soundbar` folder to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **"+ Add Integration"**
3. Search for **"LG Soundbar"**
4. Enter your soundbar's configuration:
   - **IP Address**: The IP address of your LG soundbar on your network
   - **Port**: Usually 9741 (default)
   - **Name**: A friendly name for your soundbar

The integration will attempt to connect to your soundbar and verify the connection before completing setup.

## Usage

After configuration, a new media player entity will be created (e.g., `media_player.lg_soundbar`). You can use it to:

- **Control Volume**: Use the volume slider or +/- buttons
- **Mute/Unmute**: Toggle mute status
- **Change Input Source**: Select from available inputs (HDMI, Optical, Bluetooth, etc.)
- **Select Sound Mode**: Choose equalizer presets (Standard, Bass, Cinema, Music, etc.)

### Lovelace Card Example

```yaml
type: media-control
entity: media_player.lg_soundbar
```

### Example Automations

**Turn on soundbar when TV turns on:**
```yaml
automation:
  - alias: "Sync soundbar with TV"
    trigger:
      - platform: state
        entity_id: media_player.tv
        to: "on"
    action:
      - service: media_player.select_source
        target:
          entity_id: media_player.lg_soundbar
        data:
          source: "HDMI"
```

**Lower volume at night:**
```yaml
automation:
  - alias: "Lower soundbar volume at night"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: media_player.volume_set
        target:
          entity_id: media_player.lg_soundbar
        data:
          volume_level: 0.3
```

**Auto-select cinema mode for movies:**
```yaml
automation:
  - alias: "Cinema mode for Plex"
    trigger:
      - platform: state
        entity_id: media_player.plex
        to: "playing"
    action:
      - service: media_player.select_sound_mode
        target:
          entity_id: media_player.lg_soundbar
        data:
          sound_mode: "Cinema"
```

## Protocol Details

This integration uses the proprietary LG soundbar protocol based on the work from the [temescal library](https://github.com/google/python-temescal). Communication is encrypted using AES encryption with predefined keys.

The protocol uses:
- **Port**: 9741 (default)
- **Transport**: TCP socket
- **Encryption**: AES-256-CBC with fixed IV and key
- **Format**: JSON messages with encrypted payload

## Troubleshooting

### Can't Find Soundbar

1. Ensure your soundbar is powered on and connected to your network
2. Check that your soundbar has WiFi or Ethernet connected
3. Verify the IP address is correct (check your router's DHCP leases)
4. Try pinging the IP address from your Home Assistant server

### Connection Failed

1. Make sure port 9741 is accessible (no firewall blocking)
2. Restart your soundbar
3. Check Home Assistant logs for detailed error messages:
   ```yaml
   logger:
     default: info
     logs:
       custom_components.lg_soundbar: debug
   ```

### Commands Not Working

1. Enable debug logging (see above)
2. Check if your soundbar model is compatible
3. Some features may be model-specific
4. Create an issue on GitHub with your logs and soundbar model

### Finding Your Soundbar's IP Address

- Check your router's connected devices list
- Use a network scanner app (e.g., Fing, nmap)
- Check the soundbar's network settings menu (if available)

## Supported Features

| Feature | Supported |
|---------|-----------|
| Volume Control | ✅ |
| Mute/Unmute | ✅ |
| Input Source Selection | ✅ |
| Sound Mode/EQ Selection | ✅ |
| Bass/Treble Control | ⚠️ Model Dependent |
| Woofer Level | ⚠️ Model Dependent |
| Night Mode | ⚠️ Model Dependent |
| Power On/Off | ❌ Not supported by protocol |

## Contributing

Contributions are welcome! If you have:
- Bug fixes
- Feature improvements
- Support for additional soundbar models
- Better error handling

Please submit a pull request or open an issue.

## Credits

This integration is based on the reverse-engineered LG soundbar protocol from:
- [pve84/lg_soundbar](https://github.com/pve84/lg_soundbar) - Original Home Assistant integration
- [Google Temescal](https://github.com/google/python-temescal) - Original Python library

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This is an unofficial integration and is not affiliated with or endorsed by LG Electronics. Use at your own risk.
