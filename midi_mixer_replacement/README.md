# Beginner's Guide: MIDI Mixer for Windows 11

## Step-by-Step Setup for Non-Coders

### 1. Install Python
1. Download Python from [python.org/downloads](https://www.python.org/downloads/)
2. Run the installer
3. Check "Add Python to PATH" at the bottom
4. Click "Install Now"

### 2. Get the MIDI Mixer Files
1. Download the ZIP file from [github link]
2. Right-click → "Extract All"
3. Remember where you extracted the folder

### 3. Install Required Software
1. Open the Start menu
2. Type "Command Prompt"
3. Right-click → "Run as administrator"
4. Type exactly (press Enter after each line):
```cmd
cd path\to\extracted\folder
pip install -r requirements.txt
```
(Replace "path\to\extracted\folder" with the actual location)

### 4. Connect Your MIDI Controller
1. Plug in your Akai LPD8 via USB
2. Windows will install drivers automatically

### 5. Configure Audio Devices
1. Right-click the speaker icon → "Sound settings"
2. Note the exact names of your headphones/speakers
3. Open the MIDI Mixer folder
4. Edit `config.json` with Notepad:
   - Change "Headphones" and "Speakers" to your actual device names
   - Save the file

### 6. Run the Mixer
1. In File Explorer, go to the MIDI Mixer folder
2. Hold Shift and right-click empty space
3. Select "Open in Terminal"
4. Type:
```cmd
python midi_mixer_v2.py
```

### First-Time Setup Complete!
The mixer will now respond to your MIDI controller buttons/knobs.

> **Tip**: To run automatically at startup:
> 1. Right-click in the folder → New → Shortcut
> 2. Type: `pythonw.exe midi_mixer_v2.py`
> 3. Name it "MIDI Mixer"
> 4. Press Win+R, type "shell:startup", and drag the shortcut there

## Key Features
- 🎛️ Full MIDI mapping configuration via config.json
- 🔊 Per-application volume control (Spotify, Discord, Chrome, etc.)
- 🎧 Audio device switching with custom device names
- ⏯️ Media transport controls (play/pause, next/previous track)
- 🚀 Application launcher integration
- 🛡️ Automatic error recovery and fallback defaults

## Installation (Windows 11)
1. Install Python 3.10+ (64-bit) from [python.org](https://python.org)
   - Check "Add Python to PATH" during installation
2. Open Command Prompt as Administrator:
   ```cmd
   pip install -r requirements.txt
   ```
3. Connect your Akai LPD8 controller via USB
4. Recommended Windows 11 settings:
   - Disable "Enhance audio" in Sound Settings
   - Set your preferred audio device as default
   - Grant microphone access if using mute_mic feature

## Configuration
1. Edit `config.json` to:
   - Set your actual audio device names
   - Customize MIDI mappings
   - Add/remove applications
2. Supported action types:
   - `previous_track`, `play_pause`, `next_track`
   - `switch_device:YourDeviceName`
   - `launch:app.exe`
   - `mute_mic`
   - `volume:target` (master/spotify/discord/etc.)

## Usage (Windows 11)
Run normally:
```cmd
python midi_mixer_v2.py
```

For background operation:
```cmd
start /B pythonw midi_mixer_v2.py
```

Windows 11 Pro Tip: Create a shortcut with:
- Target: `pythonw.exe midi_mixer_v2.py`
- Run: Minimized
- Add to Startup folder for automatic launch

## Troubleshooting (Windows 11)
- Run as Administrator if you get permission errors
- Check Windows Sound settings:
  - Right-click speaker icon → Open Sound settings
  - Verify device names match config.json exactly
- For MIDI issues:
  - Open "MIDI Control Panel" (search in Start)
  - Verify LPD8 appears under MIDI devices
- Common fixes:
  - Restart Windows Audio service
  - Reconnect MIDI controller
  - Update audio drivers

## Advanced
- Create a shortcut to launch at startup
- Package as executable using PyInstaller
- Extend with custom Python scripts for advanced functionality
