"""
MIDI Mixer Replacement v2.0 - Cross Platform
Complete implementation with configuration support
"""

import mido
try:
    import pyautogui
    GUI_AVAILABLE = True
except Exception as e:
    print(f"GUI not available: {e}")
    GUI_AVAILABLE = False
import subprocess
import time
import json
import os
import re
import platform
import sys

# Platform specific imports
if platform.system() == 'Windows':
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume, ISimpleAudioVolume
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    import pythoncom
    import pywintypes
    import win32com.client
    import win32gui
    import win32con
else:
    import pulsectl

class MidiMixer:
    def __init__(self):
        self.config = self.load_config()
        self.devices = self.config['audio_devices']
        self.mappings = self.config['midi_mappings']
        self.sessions = {
            'spotify': None,
            'discord': None,
            'chrome': None,
            'mic': None
        }
        self.setup_audio()
        
    def load_config(self):
        """Load configuration from JSON file with fallback defaults"""
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        try:
            with open(config_path) as f:
                config = json.load(f)
            if not all(k in config for k in ['audio_devices', 'midi_mappings']):
                raise ValueError("Invalid config structure")
            return config
        except Exception as e:
            print(f"Error loading config: {e}")
            return {
                'audio_devices': {
                    'Headphones': 'Headphones',
                    'Desk Speakers': 'Speakers'
                },
                'midi_mappings': {
                    'pads': {
                        '36': 'previous_track',
                        '37': 'play_pause',
                        '38': 'next_track',
                        '39': 'switch_device:Headphones',
                        '40': 'launch:spotify.exe',
                        '41': 'mute_mic',
                        '42': 'launch:discord.exe',
                        '43': 'switch_device:Desk Speakers'
                    },
                    'knobs': {
                        '1': 'volume:spotify',
                        '2': 'volume:discord',
                        '3': 'volume:mic',
                        '4': 'volume:master',
                        '5': 'volume:chrome',
                        '6': 'volume:app1',
                        '7': 'volume:app2',
                        '8': 'volume:master'
                    }
                }
            }

    def setup_audio(self):
        """Initialize audio control interfaces"""
        if platform.system() == 'Windows':
            try:
                self.audio_devices = AudioUtilities.GetSpeakers()
                interface = self.audio_devices.Activate(
                    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                self.master_volume = cast(interface, POINTER(IAudioEndpointVolume))
                self.update_sessions()
            except Exception as e:
                print(f"Audio control initialization failed: {e}")
                self.master_volume = None
        else:
            try:
                self.pulse = pulsectl.Pulse('midi-mixer')
                self.update_sessions()
            except Exception as e:
                print(f"PulseAudio connection failed: {e}")
                self.pulse = None

    def update_sessions(self):
        """Refresh audio session controls for applications"""
        if platform.system() == 'Windows':
            for session in AudioUtilities.GetAllSessions():
                if session.Process:
                    name = session.Process.name().lower().replace('.exe', '')
                    if name in self.sessions:
                        self.sessions[name] = session
        else:
            for sink in self.pulse.sink_input_list():
                app_name = sink.proplist.get('application.name', '').lower()
                if app_name in self.sessions:
                    self.sessions[app_name] = sink

    def set_volume(self, target, value):
        """Set volume for specific application or master"""
        try:
            if platform.system() == 'Windows':
                if self.master_volume and target == 'master':
                    self.master_volume.SetMasterVolumeLevelScalar(value, None)
                elif target in self.sessions and self.sessions[target]:
                    volume = self.sessions[target]._ctl.QueryInterface(ISimpleAudioVolume)
                    volume.SetMasterVolume(value, None)
            else:
                if self.pulse and target == 'master':
                    sink = self.pulse.get_sink_by_name(self.pulse.server_info().default_sink_name)
                    self.pulse.volume_set_all_chans(sink, value)
                elif target in self.sessions and self.sessions[target]:
                    self.pulse.volume_set_all_chans(self.sessions[target], value)
        except Exception as e:
            print(f"Volume control failed: {e}")

    def switch_output_device(self, device_name):
        """Switch default audio output device"""
        if platform.system() == 'Windows':
            try:
                pythoncom.CoInitialize()
                dev_enum = win32com.client.Dispatch("{BCDE0395-E52F-467C-8E3D-C4579291692E}")
                devices = dev_enum.EnumAudioEndpoints(0, 1)  # eRender, DEVICE_STATE_ACTIVE
                
                for i in range(devices.Count):
                    dev = devices.Item(i)
                    if self.devices[device_name] in dev.GetName():
                        policy_config = win32com.client.Dispatch("{870AF99C-171D-4F9E-AF0D-E63DF40C2BC9}")
                        policy_config.SetDefaultEndpoint(dev.GetId(), 0)
                        print(f"Switched to {device_name}")
                        return True
                
                print(f"Device {device_name} not found")
                return False
            except Exception as e:
                print(f"Error switching device: {e}")
                return False
        else:
            try:
                sinks = self.pulse.sink_list()
                for sink in sinks:
                    if self.devices[device_name].lower() in sink.description.lower():
                        self.pulse.default_set(sink)
                        print(f"Switched to {device_name}")
                        return True
                print(f"Device {device_name} not found")
                return False
            except Exception as e:
                print(f"Error switching device: {e}")
                return False

    def handle_midi(self, msg):
        """Process incoming MIDI messages"""
        if msg.type == 'note_on':
            action = self.mappings['pads'].get(str(msg.note))
            if action:
                if action == 'previous_track' and GUI_AVAILABLE:
                    pyautogui.press('prevtrack')
                elif action == 'play_pause' and GUI_AVAILABLE:
                    pyautogui.press('playpause')
                elif action == 'next_track' and GUI_AVAILABLE:
                    pyautogui.press('nexttrack')
                elif action.startswith('switch_device:'):
                    self.switch_output_device(action.split(':')[1])
                elif action.startswith('launch:'):
                    subprocess.Popen([action.split(':')[1]])
                elif action == 'mute_mic' and GUI_AVAILABLE:
                    pyautogui.press('volumemute')

        elif msg.type == 'control_change':
            action = self.mappings['knobs'].get(str(msg.control))
            if action and action.startswith('volume:'):
                self.set_volume(action.split(':')[1], msg.value / 127.0)

    def run(self):
        """Main application loop"""
        try:
            midi_input = None
            for name in mido.get_input_names():
                if "LPD8" in name:
                    midi_input = name
                    break

            if not midi_input:
                print("Akai LPD8 not found. Please connect your device.")
                return

            print(f"Connected to MIDI device: {midi_input}")
            print("Running MIDI mixer replacement...")

            with mido.open_input(midi_input) as inport:
                for msg in inport:
                    self.handle_midi(msg)
                    self.update_sessions()
        except Exception as e:
            print(f"MIDI initialization failed: {e}")
            print("Running in demo mode without MIDI input")
            while True:
                time.sleep(1)  # Keep process alive

if __name__ == "__main__":
    mixer = MidiMixer()
    mixer.run()
