from fpdf import FPDF
from datetime import datetime
import os

class HDexDoc(FPDF):
    def header(self):
        self.set_fill_color(2, 6, 23)
        self.rect(0, 0, 210, 40, 'F')
        self.set_font('helvetica', 'B', 24)
        self.set_text_color(255, 0, 0) # Danger Red
        self.cell(0, 25, 'H-DEX ULTRA: DANGER EDITION v5.0', ln=True, align='C')
        self.set_font('helvetica', 'I', 10)
        self.set_text_color(255, 255, 255)
        self.cell(0, -10, 'The Ultimate Administrative Chaos & Security Suite', ln=True, align='C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'H-DEX ULTRA DANGER | Page {self.page_no()} | Generated on {datetime.now().strftime("%Y-%m-%d")}', align='C')

    def chapter_title(self, title):
        self.set_font('helvetica', 'B', 16)
        self.set_fill_color(255, 0, 0)
        self.set_text_color(255, 255, 255)
        self.cell(0, 12, f'  {title}', ln=True, align='L', fill=True)
        self.ln(5)

    def chapter_body(self, body):
        self.set_font('helvetica', '', 11)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 7, body)
        self.ln()

pdf = HDexDoc()
pdf.add_page()

pdf.chapter_title("1. THE DANGER MODE: SYSTEM CHAOS")
pdf.chapter_body(
    "- Full Lockdown: Task Manager and Desktop Icons are instantly disabled.\n"
    "- Atmospheric Nightmare: Injects custom wallpaper and scheduled sound effects from the 'dengraose' folder.\n"
    "- Punishment Prompt: Automatically deploys a permanent instructional notepad on the client desktop.\n"
    "- Recovery Mission: An interactive, multi-stage game that the client must complete to restore system normalcy.\n"
    "- Jumpscare Engine: Random full-screen visual flashes to maintain psychological dominance during focus."
)

pdf.chapter_title("2. STEALTH & PERSISTENCE")
pdf.chapter_body(
    "- Anti-Debugging: Active detection for debuggers and VM analysts; the process terminates instantly if detected.\n"
    "- Registry Persistence: Automatically sets up as a 'Windows Health Monitor' in the current user's auto-run registry.\n"
    "- Discord Bot Integration: Full /danger command support for remote chaos management from any mobile device.\n"
    "- Admin Dashboard Guard: Direct Danger Mode triggers added to both the Prank and Admin Tools tabs."
)

pdf.chapter_title("3. ADVANCED DATA RECOVERY (v5.0)")
pdf.chapter_body(
    "- Credit Card Extractor: Deep scan for browser-saved payment methods.\n"
    "- Registry God-Mode: Full control over HKLM, HKCU, and critical system hives.\n"
    "- Master Discovery: Identifying all browser extensions, local users, and network topology."
)

pdf.set_font('helvetica', 'B', 12)
pdf.set_text_color(255, 0, 0)
pdf.cell(0, 10, "FOR AUTHORIZED ADMINISTRATIVE & SECURITY TESTING ONLY.", ln=True, align='C')

output_path = os.path.join("RedMeFast", "README_DANGER_v50.pdf")
if not os.path.exists("RedMeFast"): os.makedirs("RedMeFast")
pdf.output(output_path)
print(f"Danger Edition Docs generated at {output_path}")
