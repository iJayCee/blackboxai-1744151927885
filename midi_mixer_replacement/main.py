import mido
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume, ISimpleAudioVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import pyautogui
import subprocess
import time

# Audio setup
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
master_volume = cast(interface, POINTER(IAudioEndpointVolume))

# Audio sessions for app-specific control
sessions = {
    'spotify': None,
    'discord': None,
    'chrome': None,
    'mic': None
}

def get_audio_session(process_name):
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        if session.Process and session.Process.name().lower() == f"{process_name}.exe":
            return session
    return None

def update_sessions():
    sessions['spotify'] = get_audio_session('spotify')
    sessions['discord'] = get_audio_session('discord')
    sessions['chrome'] = get_audio_session('chrome')
    sessions['mic'] = get_audio_session('discord')  # Assuming mic is through Discord

# MIDI device setup
def find_lpd8():
    for name in mido.get_input_names():
        if "LPD8" in name:
            return name
    return None

# Volume control functions
def set_volume(session, value):
    if session:
        volume = session._ctl.QueryInterface(ISimpleAudioVolume)
        volume.SetMasterVolume(value, None)

def set_master_volume(value):
    master_volume.SetMasterVolumeLevelScalar(value, None)

# Device switching
import ctypes
from ctypes import wintypes
import pythoncom
import pywintypes
import win32com.client
import win32gui
import win32con

# Predefined device names (update these to match your actual device names)
DEVICES = {
    'Headphones': 'Your Headphone Device Name',
    'Desk Speakers': 'Your Speaker Device Name'
}

def switch_output_device(device_name):
    """Switch default audio output device using Windows Core Audio API"""
    try:
        pythoncom.CoInitialize()
        dev_enum = win32com.client.Dispatch("{BCDE0395-E52F-467C-8E3D-C4579291692E}")
        devices = dev_enum.EnumAudioEndpoints(0, 1)  # eRender, DEVICE_STATE_ACTIVE
        
        for i in range(devices.Count):
            dev = devices.Item(i)
            if DEVICES[device_name] in dev.GetName():
                # Get the policy config COM object
                policy_config = win32com.client.Dispatch("{870AF99C-171D-4F9E-AF0D-E63DF40C2BC9}")
                # Set as default device
                policy_config.SetDefaultEndpoint(dev.GetId(), 0)  # eRender
                print(f"Successfully switched to {device_name}")
                return True
        
        print(f"Device {device_name} not found")
        return False
    except Exception as e:
        print(f"Error switching device: {e}")
        return False

# Main MIDI handler
def handle_midi_message(msg):
    print(f"MIDI: {msg}")
    
    # Pad handlers
    if msg.type == 'note_on':
        if msg.note == 36:  # Pad 1 - Previous song
            pyautogui.press('prevtrack')
        elif msg.note == 37:  # Pad 2 - Play/Pause
            pyautogui.press('playpause')
        elif msg.note == 38:  # Pad 3 - Next song
            pyautogui.press('nexttrack')
        elif msg.note == 39:  # Pad 4 - Switch to Headphones
            switch_output_device('Headphones')
        elif msg.note == 40:  # Pad 5 - Launch Spotify
            subprocess.Popen(["spotify.exe"])
        elif msg.note == 41:  # Pad 6 - Mute mic
            pyautogui.press('volumemute')  # May need adjustment
        elif msg.note == 42:  # Pad 7 - Launch Discord
            subprocess.Popen(["discord.exe"])
        elif msg.note == 43:  # Pad 8 - Switch to Desk Speakers
            switch_output_device('Desk Speakers')
    
    # Knob handlers (CC messages)
    elif msg.type == 'control_change':
        value = msg.value / 127.0  # Convert to 0-1 range
        
        if msg.control == 1:  # Knob 1 - Spotify volume
            set_volume(sessions['spotify'], value)
        elif msg.control == 2:  # Knob 2 - Discord volume
            set_volume(sessions['discord'], value)
        elif msg.control == 3:  # Knob 3 - Mic volume
            set_volume(sessions['mic'], value)
        elif msg.control == 4:  # Knob 4 - Master volume
            set_master_volume(value)
        elif msg.control == 5:  # Knob 5 - Chrome volume
            set_volume(sessions['chrome'], value)
        elif msg.control == 6:  # Knob 6 - App volume 1
            pass  # Implement as needed
        elif msg.control == 7:  # Knob 7 - App volume 2
            pass  # Implement as needed
        elif msg.control == 8:  # Knob 8 - Master volume
            set_master_volume(value)

def main():
    update_sessions()
    midi_input = find_lpd8()
    
    if not midi_input:
        print("Akai LPD8 not found. Please connect your device.")
        return
    
    print(f"Connected to MIDI device: {midi_input}")
    print("Running MIDI mixer replacement...")
    
    with mido.open_input(midi_input) as inport:
        for msg in inport:
            handle_midi_message(msg)
            update_sessions()  # Refresh audio sessions periodically

if __name__ == "__main__":
    main()
