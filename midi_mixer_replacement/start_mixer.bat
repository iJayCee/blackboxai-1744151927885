@echo off
title MIDI Mixer Replacement
echo Starting MIDI Mixer Replacement...
echo Press Ctrl+C to stop

:: Check if running as admin, restart if not
NET SESSION >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo Running with admin privileges
) else (
    echo Requesting admin privileges...
    powershell -Command "Start-Process cmd -ArgumentList '/c %~dpnx0' -Verb RunAs"
    exit /b
)

:: Run the mixer in background
start /B pythonw midi_mixer_v2.py

echo Application started in background
echo You can close this window
pause
