"""
╔══════════════════════════════════════════════════════╗
║          H-DEX UNIVERSAL REMOVER v2.0                ║
║   Complete Forensic-Grade Client Removal Tool        ║
╚══════════════════════════════════════════════════════╝
"""

import os
import subprocess
import winreg
import ctypes
import ctypes.wintypes
import time
import sys
import shutil
import glob
import datetime
import traceback

try:
    import psutil
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil", "-q"])
    import psutil

# ─────────────── INJECTED CONFIGURATION ───────────────
STARTUP_KEY_NAME = "{STARTUP_KEY_NAME}"
ENABLE_CRITICAL = {ENABLE_CRITICAL}
# ──────────────────────────────────────────────────────

# Known H-Dex hidden directory names (NEVER system folders)
HDEX_DIR_NAMES = [
    "H-DexClient",
    "H-Dex-Network",
    r"Microsoft\RuntimeBroker",
    r"Microsoft\Windows\SystemApps",
    ".sys_config",
    ".win_update",
    ".data_cache",
]

# Known H-Dex process executable names
HDEX_PROCESS_NAMES = [
    STARTUP_KEY_NAME.lower().replace(" ", "") + ".exe",
    STARTUP_KEY_NAME.lower() + ".exe",
    # Note: We do NOT explicitly list generically named payloads here (like runtimebroker.exe or varying custom names)
    # to avoid killing legitimate Windows processes. They are caught automatically
    # by the directory check below if running from a hidden APPDATA directory.
]

NORMAL_ATTR   = 0x80  # FILE_ATTRIBUTE_NORMAL
HIDDEN_SYSTEM = 0x06  # FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_SYSTEM

# ─────────────── CONSOLE COLOR HELPERS ────────────────
class C:
    """ANSI color codes for Windows 10+ console."""
    R  = "\033[91m"   # Red
    G  = "\033[92m"   # Green
    Y  = "\033[93m"   # Yellow
    B  = "\033[94m"   # Blue
    M  = "\033[95m"   # Magenta
    CY = "\033[96m"   # Cyan
    W  = "\033[97m"   # White
    DIM = "\033[90m"  # Dim/Gray
    BOLD = "\033[1m"
    END = "\033[0m"

# Enable ANSI on Windows
os.system("")

# ─────────────── LOGGING ──────────────────────────────
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hdex_removal_log.txt")
log_lines = []

def log(msg, color="", symbol="+"):
    """Print & log a message."""
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    clean = f"[{ts}] [{symbol}] {msg}"
    log_lines.append(clean)

    prefix_map = {"+": C.G, "-": C.R, "!": C.Y, "*": C.CY, "~": C.M, "✓": C.G, "✗": C.R}
    col = color or prefix_map.get(symbol, C.W)
    print(f"  {col}[{symbol}]{C.END} {msg}")

def save_log():
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("H-DEX UNIVERSAL REMOVER – REMOVAL LOG\n")
            f.write(f"Date: {datetime.datetime.now().isoformat()}\n")
            f.write("=" * 55 + "\n\n")
            f.write("\n".join(log_lines))
        print(f"\n  {C.DIM}Log saved to: {LOG_FILE}{C.END}")
    except:
        pass


# ─────────────── UTILITIES ────────────────────────────

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def elevate():
    print(f"  {C.Y}[*] Requesting Administrator privileges...{C.END}")
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )
    sys.exit()

def enable_debug_privilege():
    """Enable SeDebugPrivilege for the current process."""
    try:
        token = ctypes.wintypes.HANDLE()
        ctypes.windll.advapi32.OpenProcessToken(
            ctypes.windll.kernel32.GetCurrentProcess(),
            0x0020 | 0x0008,
            ctypes.byref(token),
        )

        class LUID(ctypes.Structure):
            _fields_ = [("LowPart", ctypes.wintypes.DWORD), ("HighPart", ctypes.c_long)]

        class LUID_AND_ATTRIBUTES(ctypes.Structure):
            _fields_ = [("Luid", LUID), ("Attributes", ctypes.wintypes.DWORD)]

        class TOKEN_PRIVILEGES(ctypes.Structure):
            _fields_ = [("PrivilegeCount", ctypes.wintypes.DWORD), ("Privileges", LUID_AND_ATTRIBUTES * 1)]

        luid = LUID()
        ctypes.windll.advapi32.LookupPrivilegeValueW(None, "SeDebugPrivilege", ctypes.byref(luid))

        tp = TOKEN_PRIVILEGES()
        tp.PrivilegeCount = 1
        tp.Privileges[0].Luid = luid
        tp.Privileges[0].Attributes = 0x00000002

        ctypes.windll.advapi32.AdjustTokenPrivileges(token, False, ctypes.byref(tp), 0, None, None)
        ctypes.windll.kernel32.CloseHandle(token)
        log("SeDebugPrivilege enabled.", symbol="+")
        return True
    except Exception as e:
        log(f"Could not enable SeDebugPrivilege: {e}", symbol="-")
        return False

def unhide_recursive(path):
    """Recursively reset file attributes to NORMAL so deletion works."""
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            fp = os.path.join(root, name)
            try:
                ctypes.windll.kernel32.SetFileAttributesW(fp, NORMAL_ATTR)
            except:
                pass
        for name in dirs:
            fp = os.path.join(root, name)
            try:
                ctypes.windll.kernel32.SetFileAttributesW(fp, NORMAL_ATTR)
            except:
                pass
    ctypes.windll.kernel32.SetFileAttributesW(path, NORMAL_ATTR)

def safe_delete_tree(path):
    """Unhide, then delete an entire directory tree."""
    if not os.path.exists(path):
        return False
    unhide_recursive(path)
    shutil.rmtree(path, ignore_errors=True)
    if os.path.exists(path):
        # If still exists (locked files), mark for reboot deletion
        ctypes.windll.kernel32.MoveFileExW(path, None, 0x04)
        log(f"Locked – marked for deletion on reboot: {path}", symbol="~")
    return True

def safe_delete_file(path):
    """Unhide, then delete a single file."""
    if not os.path.exists(path):
        return False
    try:
        ctypes.windll.kernel32.SetFileAttributesW(path, NORMAL_ATTR)
        os.remove(path)
        return True
    except PermissionError:
        ctypes.windll.kernel32.MoveFileExW(path, None, 0x04)
        log(f"Locked – marked for deletion on reboot: {path}", symbol="~")
        return True
    except Exception:
        return False


# ═══════════════════════════════════════════════════════
#  STEP 1 – Disable Critical Flag & Kill All Processes
# ═══════════════════════════════════════════════════════

def step_1_kill_processes():
    header("STEP 1", "Disabling Critical Process & Killing Client")
    enable_debug_privilege()

    ntdll   = ctypes.windll.ntdll
    kernel32 = ctypes.windll.kernel32
    PROCESS_ALL_ACCESS = 0x1F0FFF

    killed_pids = set()

    for proc in psutil.process_iter(["pid", "name", "exe", "cmdline"]):
        try:
            pname = (proc.info.get("name") or "").lower()
            pexe  = (proc.info.get("exe") or "").lower()

            is_hdex = False
            for known in HDEX_PROCESS_NAMES:
                if known in pname or known in pexe:
                    is_hdex = True
                    break

            # Also match anything running from known H-Dex directories
            if not is_hdex:
                for dname in HDEX_DIR_NAMES:
                    if dname.lower() in pexe:
                        is_hdex = True
                        break

            if not is_hdex:
                continue

            pid = proc.info["pid"]
            if pid in killed_pids or pid == os.getpid():
                continue

            log(f"Found H-Dex process: {C.BOLD}{pname}{C.END} (PID {pid})", symbol="!")

            # Remove critical process flag
            hProcess = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
            if hProcess:
                val = ctypes.c_ulong(0)
                status = ntdll.NtSetInformationProcess(hProcess, 0x1D, ctypes.byref(val), ctypes.sizeof(val))
                if status == 0:
                    log(f"Critical flag REMOVED from PID {pid} – safe to kill.", symbol="✓")
                else:
                    log(f"NtSetInformationProcess returned 0x{status:08X}", symbol="!")
                kernel32.CloseHandle(hProcess)

            # Kill entire process tree (parent + children)
            try:
                parent = psutil.Process(pid)
                children = parent.children(recursive=True)
                for child in children:
                    try:
                        child.kill()
                        log(f"Killed child process: {child.name()} (PID {child.pid})", symbol="+")
                        killed_pids.add(child.pid)
                    except:
                        pass
                parent.kill()
                parent.wait(timeout=5)
            except:
                pass

            log(f"Process PID {pid} terminated – {C.G}NO BSOD{C.END}.", symbol="✓")
            killed_pids.add(pid)

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
        except Exception as e:
            log(f"Process error: {e}", symbol="-")

    if not killed_pids:
        log("No active H-Dex processes found (already stopped).", symbol="*")

    # Brief pause for OS to release file locks
    time.sleep(1)


# ═══════════════════════════════════════════════════════
#  STEP 2 – Remove All Persistence Entries
# ═══════════════════════════════════════════════════════

def step_2_remove_persistence():
    header("STEP 2", "Stripping All Persistence Mechanisms")

    # 2a. Registry Run Key
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, STARTUP_KEY_NAME)
        log("Removed Registry Run Key.", symbol="✓")
    except FileNotFoundError:
        log("Registry Run Key not present (clean).", symbol="*")
    except Exception as e:
        log(f"Registry error: {e}", symbol="-")

    # 2b. HKCU\Environment UserInitMprLogonScript
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, "UserInitMprLogonScript")
        log("Removed HKCU\\Environment UserInitMprLogonScript.", symbol="✓")
    except FileNotFoundError:
        log("Environment key not present (clean).", symbol="*")
    except Exception as e:
        log(f"Environment error: {e}", symbol="-")

    # 2c. Scheduled Task
    try:
        out = subprocess.run(f'schtasks /delete /tn "{STARTUP_KEY_NAME}" /f', shell=True, capture_output=True, text=True)
        if "ERROR" not in out.stderr:
            log("Removed Scheduled Task.", symbol="✓")
        else:
            log("Scheduled Task not present (clean).", symbol="*")
    except Exception as e:
        log(f"Task Scheduler error: {e}", symbol="-")

    # 2d. Startup Folder Drop
    appdata = os.getenv("APPDATA")
    bat_path = os.path.join(appdata, r"Microsoft\Windows\Start Menu\Programs\Startup", f"{STARTUP_KEY_NAME}.bat")
    if safe_delete_file(bat_path):
        log("Removed Startup Folder Drop (.bat).", symbol="✓")
    else:
        log("Startup .bat not present (clean).", symbol="*")


# ═══════════════════════════════════════════════════════
#  STEP 3 – Reverse Windows Defender Exclusions
# ═══════════════════════════════════════════════════════

def step_3_defender_cleanup():
    header("STEP 3", "Reversing Windows Defender Exclusions")

    appdata = os.getenv("APPDATA")
    paths_to_check = [
        os.path.join(appdata, "H-DexClient"),
        os.path.join(appdata, "H-Dex-Network"),
        os.path.join(appdata, r"Microsoft\RuntimeBroker"),
        os.path.join(appdata, r"Microsoft\Windows\SystemApps"),
    ]

    removed_any = False
    for path in paths_to_check:
        try:
            result = subprocess.run(
                f'powershell -Command "Remove-MpPreference -ExclusionPath \'{path}\' -ErrorAction SilentlyContinue"',
                shell=True, capture_output=True, text=True, timeout=15
            )
            if result.returncode == 0:
                log(f"Removed Defender exclusion: {path}", symbol="✓")
                removed_any = True
        except subprocess.TimeoutExpired:
            log("Defender command timed out (non-critical).", symbol="!")
        except Exception as e:
            log(f"Defender cleanup error: {e}", symbol="-")

    if not removed_any:
        log("No Defender exclusions found to remove.", symbol="*")


# ═══════════════════════════════════════════════════════
#  STEP 4 – Find & Destroy Hidden Directories
# ═══════════════════════════════════════════════════════

def step_4_remove_directories():
    header("STEP 4", "Sweeping Hidden Client Directories")

    appdata      = os.getenv("APPDATA")
    localappdata = os.getenv("LOCALAPPDATA")
    userprofile  = os.getenv("USERPROFILE")
    temp         = os.getenv("TEMP")
    programdata  = os.getenv("PROGRAMDATA")

    scan_roots = list(filter(None, [appdata, localappdata, userprofile, temp, programdata]))

    found_any = False
    for scan_root in scan_roots:
        for dirname in HDEX_DIR_NAMES:
            full_path = os.path.join(scan_root, dirname)
            if os.path.exists(full_path):
                found_any = True
                log(f"Found: {C.Y}{full_path}{C.END}", symbol="!")
                if safe_delete_tree(full_path):
                    log(f"Deleted: {full_path}", symbol="✓")
                else:
                    log(f"Failed to delete: {full_path}", symbol="-")

    if not found_any:
        log("No hidden H-Dex directories found.", symbol="*")


# ═══════════════════════════════════════════════════════
#  STEP 5 – Deep Scan for Leftover Executables
# ═══════════════════════════════════════════════════════

def step_5_scan_leftovers():
    header("STEP 5", "Deep Scanning for Leftover Artifacts")

    appdata      = os.getenv("APPDATA")
    localappdata = os.getenv("LOCALAPPDATA")
    temp         = os.getenv("TEMP")
    userprofile  = os.getenv("USERPROFILE")

    exe_patterns = []
    for name in HDEX_PROCESS_NAMES:
        exe_patterns.append(f"**/{name}")

    found = False
    for base in filter(None, [appdata, localappdata, temp]):
        for pattern in exe_patterns:
            try:
                for match in glob.glob(os.path.join(base, pattern), recursive=True):
                    found = True
                    log(f"Leftover executable: {C.Y}{match}{C.END}", symbol="!")
                    if safe_delete_file(match):
                        log(f"Deleted: {match}", symbol="✓")
            except Exception:
                pass

    # Also scan for .bat droppers with our name
    startup_dir = os.path.join(appdata, r"Microsoft\Windows\Start Menu\Programs\Startup")
    if os.path.exists(startup_dir):
        for f in os.listdir(startup_dir):
            if STARTUP_KEY_NAME.lower() in f.lower() or "h-dex" in f.lower():
                fp = os.path.join(startup_dir, f)
                if safe_delete_file(fp):
                    found = True
                    log(f"Deleted startup dropper: {fp}", symbol="✓")

    # Clean up any .spec / build artifacts left by PyInstaller in Desktop
    desktop = os.path.join(userprofile, "Desktop")
    for pattern in ["*.spec"]:
        for match in glob.glob(os.path.join(desktop, "**", pattern), recursive=True):
            if "h-dex" in match.lower() or STARTUP_KEY_NAME.lower().replace(" ", "") in match.lower():
                safe_delete_file(match)
                log(f"Cleaned build artifact: {match}", symbol="✓")
                found = True

    if not found:
        log("No leftover files found.", symbol="*")


# ═══════════════════════════════════════════════════════
#  STEP 6 – Prefetch & Recent Traces Cleanup
# ═══════════════════════════════════════════════════════

def step_6_clean_traces():
    header("STEP 6", "Cleaning Prefetch & System Traces")

    # Prefetch files
    prefetch_dir = r"C:\Windows\Prefetch"
    cleaned = 0
    if os.path.exists(prefetch_dir):
        try:
            for f in os.listdir(prefetch_dir):
                lower = f.lower()
                for name in HDEX_PROCESS_NAMES:
                    if name.replace(".exe", "") in lower:
                        fp = os.path.join(prefetch_dir, f)
                        try:
                            os.remove(fp)
                            cleaned += 1
                            log(f"Deleted prefetch: {f}", symbol="✓")
                        except:
                            pass
        except PermissionError:
            log("Cannot access Prefetch folder (need SYSTEM).", symbol="!")
    
    if cleaned == 0:
        log("No prefetch traces found.", symbol="*")

    # Clean temp VBS/BAT scripts the client may have dropped
    temp = os.getenv("TEMP")
    for ext in ["*.vbs", "*.bat", "*.cmd"]:
        for match in glob.glob(os.path.join(temp, ext)):
            lower = os.path.basename(match).lower()
            if "h-dex" in lower or STARTUP_KEY_NAME.lower().replace(" ", "") in lower:
                safe_delete_file(match)
                log(f"Cleaned temp script: {match}", symbol="✓")


# ═══════════════════════════════════════════════════════
#  STEP 7 – Verification Pass
# ═══════════════════════════════════════════════════════

def step_7_verify():
    header("STEP 7", "Verification Pass")
    all_clean = True

    # Check registry
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ) as key:
            try:
                winreg.QueryValueEx(key, STARTUP_KEY_NAME)
                log(f"Registry Run Key STILL EXISTS!", symbol="✗")
                all_clean = False
            except FileNotFoundError:
                log("Registry Run Key: CLEAN", symbol="✓")
    except:
        log("Registry Run Key: CLEAN", symbol="✓")

    # Check environment
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_READ) as key:
            try:
                winreg.QueryValueEx(key, "UserInitMprLogonScript")
                log(f"Environment UserInit STILL EXISTS!", symbol="✗")
                all_clean = False
            except FileNotFoundError:
                log("Environment UserInit: CLEAN", symbol="✓")
    except:
        log("Environment UserInit: CLEAN", symbol="✓")

    # Check task
    out = subprocess.run(f'schtasks /query /tn "{STARTUP_KEY_NAME}" 2>&1', shell=True, capture_output=True, text=True)
    if "ERROR" in out.stderr or "ERROR" in out.stdout:
        log("Scheduled Task: CLEAN", symbol="✓")
    else:
        log("Scheduled Task STILL EXISTS!", symbol="✗")
        all_clean = False

    # Check directories
    appdata = os.getenv("APPDATA")
    for dirname in HDEX_DIR_NAMES:
        fp = os.path.join(appdata, dirname)
        if os.path.exists(fp):
            log(f"Directory still exists: {fp}", symbol="✗")
            all_clean = False

    # Check running processes
    for proc in psutil.process_iter(["name", "exe"]):
        try:
            pname = (proc.info.get("name") or "").lower()
            pexe  = (proc.info.get("exe") or "").lower()
            for known in HDEX_PROCESS_NAMES:
                if known in pname or known in pexe:
                    log(f"Process STILL RUNNING: {pname} (PID {proc.pid})", symbol="✗")
                    all_clean = False
        except:
            pass

    return all_clean


# ═══════════════════════════════════════════════════════
#  DISPLAY HELPERS
# ═══════════════════════════════════════════════════════

def banner():
    print(f"""
{C.CY}{C.BOLD}
    ██╗  ██╗ ██████╗ ███████╗██╗  ██╗
    ██║  ██║ ██╔══██╗██╔════╝╚██╗██╔╝
    ███████║ ██║  ██║█████╗   ╚███╔╝
    ██╔══██║ ██║  ██║██╔══╝   ██╔██╗
    ██║  ██║ ██████╔╝███████╗██╔╝ ██╗
    ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝
{C.END}
{C.W}{C.BOLD}        ══ UNIVERSAL REMOVER v2.0 ══{C.END}
{C.DIM}    Complete Forensic-Grade Client Removal{C.END}
{C.DIM}    ─────────────────────────────────────{C.END}
{C.Y}  ⚠  WARNING: This will completely remove{C.END}
{C.Y}     H-Dex from this system.{C.END}
{C.DIM}    ─────────────────────────────────────{C.END}
""")

def header(step, title):
    """Print a styled step header."""
    print(f"\n  {C.CY}{'─' * 50}{C.END}")
    print(f"  {C.BOLD}{C.CY}{step}{C.END}  {C.W}{title}{C.END}")
    print(f"  {C.CY}{'─' * 50}{C.END}")

def final_summary(all_clean):
    print(f"""
  {C.CY}{'═' * 50}{C.END}
  {C.BOLD}{C.W}       H-DEX REMOVAL {"COMPLETE ✓" if all_clean else "PARTIALLY COMPLETE"}{C.END}
  {C.CY}{'═' * 50}{C.END}
  {C.G}  [✓] Critical process flag disabled (no BSOD){C.END}
  {C.G}  [✓] Client processes terminated{C.END}
  {C.G}  [✓] Registry / Env / Task / Startup cleaned{C.END}
  {C.G}  [✓] Defender exclusions reversed{C.END}
  {C.G}  [✓] Hidden directories destroyed{C.END}
  {C.G}  [✓] Leftover files scrubbed{C.END}
  {C.G}  [✓] Prefetch & traces cleaned{C.END}
  {C.G}  [✓] Verification pass {"PASSED" if all_clean else f"{C.Y}HAS WARNINGS"}{C.END}
  {C.CY}{'═' * 50}{C.END}
""")

    if not all_clean:
        print(f"  {C.Y}[!] Some items could not be removed (locked files).{C.END}")
        print(f"  {C.Y}[!] A reboot is REQUIRED to finalize removal.{C.END}")

    choice = input(f"\n  {C.M}[?]{C.END} Reboot now to finalize? ({C.G}Y{C.END}/{C.R}N{C.END}): ")
    if choice.strip().lower() == "y":
        print(f"\n  {C.CY}[*] Rebooting in 5 seconds...{C.END}")
        time.sleep(1)
        subprocess.run('shutdown /r /t 5 /c "H-Dex Uninstaller: Completing removal"', shell=True)
    else:
        print(f"\n  {C.Y}[!] Reboot skipped. Locked items will be cleaned on next restart.{C.END}")


# ═══════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    banner()

    if not is_admin():
        elevate()

    confirm = input(f"  {C.Y}[?]{C.END} Proceed with full H-Dex removal? ({C.G}Y{C.END}/{C.R}N{C.END}): ")
    if confirm.strip().lower() != "y":
        print(f"\n  {C.R}[!] Removal cancelled by user.{C.END}")
        sys.exit()

    print()

    try:
        step_1_kill_processes()       # Disable critical & kill
        step_2_remove_persistence()   # Strip all persistence
        step_3_defender_cleanup()     # Reverse Defender exclusions
        step_4_remove_directories()   # Delete hidden folders
        step_5_scan_leftovers()       # Clean remaining artifacts
        step_6_clean_traces()         # Prefetch & temp cleanup
        all_clean = step_7_verify()   # Verification sweep
    except Exception as e:
        log(f"FATAL ERROR: {e}", symbol="✗")
        traceback.print_exc()
        all_clean = False

    final_summary(all_clean)
    save_log()

    input(f"\n  {C.DIM}Press Enter to exit...{C.END}")
