#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script starts LibreOffice in the background if it is not already running.

Generated by Raymond Yee with the help of claude.ai (Aug, 2024)
"""
import subprocess
import psutil
import time
import sys

def is_libreoffice_running():
    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            # Check for both 'soffice' and 'LibreOffice' in the process name
            if 'soffice' in proc.name().lower() or 'libreoffice' in proc.name().lower():
                cmdline = proc.cmdline()
                # Check if the process has the correct command line arguments
                if any('--accept=socket,host=localhost,port=2002' in arg for arg in cmdline):
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def start_libreoffice():
    cmd = 'soffice --accept="socket,host=localhost,port=2002;urp;StarOffice.ServiceManager"'
    if sys.platform == 'darwin':  # macOS
        cmd = '/Applications/LibreOffice.app/Contents/MacOS/soffice --accept="socket,host=localhost,port=2002;urp;StarOffice.ServiceManager"'
    try:
        subprocess.Popen(cmd, shell=True, start_new_session=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    except subprocess.SubprocessError as e:
        print(f"Error starting LibreOffice: {e}")

def ensure_libreoffice_running():
    if not is_libreoffice_running():
        print("LibreOffice is not running. Starting it now...")
        start_libreoffice()
        for _ in range(10):  # Try for 10 seconds
            time.sleep(1)
            if is_libreoffice_running():
                print("LibreOffice started successfully.")
                return
        print("Failed to start LibreOffice.")
    else:
        print("LibreOffice is already running.")

if __name__ == "__main__":
    ensure_libreoffice_running()