from fpdf import FPDF
from datetime import datetime
import os

class HDexDoc(FPDF):
    def header(self):
        self.set_fill_color(15, 23, 42)
        self.rect(0, 0, 210, 40, 'F')
        self.set_font('helvetica', 'B', 24)
        self.set_text_color(244, 114, 182) # H-Dex Ultra Pink
        self.cell(0, 25, 'H-DEX ULTRA: GOD MODE v4.0', ln=True, align='C')
        self.set_font('helvetica', 'I', 10)
        self.set_text_color(255, 255, 255)
        self.cell(0, -10, 'The Ultimate Administrative God-Tier Suite', ln=True, align='C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'H-DEX ULTRA GOD MODE | Page {self.page_no()} | Generated on {datetime.now().strftime("%Y-%m-%d")}', align='C')

    def chapter_title(self, title):
        self.set_font('helvetica', 'B', 16)
        self.set_fill_color(244, 114, 182)
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

pdf.chapter_title("1. GOD MODE: LOCKDOWN TOOLS")
pdf.chapter_body(
    "- Internet Kill Switch: Disables all network adapters with one click.\n"
    "- Hardware Interlock: Lock out USB ports, Mouse, and Keyboard input remotely.\n"
    "- Defender God-Mode: Force-disable Windows Defender Real-time monitoring.\n"
    "- Input Device Suppression: Block user interaction during sensitive maintenance tasks."
)

pdf.chapter_title("2. ULTRA INTELLIGENCE & EXTRACTION")
pdf.chapter_body(
    "- Saved Credit Card Grabber: Recovers payment methods from Chrome Web Data.\n"
    "- Registry God-View: Manually explore, set, or delete any Windows Registry keys.\n"
    "- Deep Software Audit: Comprehensive scan of all installed applications and versions.\n"
    "- Network Mapping (ARP/DNS): View local network topology and DNS cache history.\n"
    "- Sensitive Doc Hunter: Automated scan for high-priority documents (.pdf, .docx, etc.)."
)

pdf.chapter_title("3. PREMIUM VISUALS & PRANKS")
pdf.chapter_body(
    "- Ultra Matrix Effect: Launches a high-performance, full-screen digital rain simulation.\n"
    "- Fake Windows Update: Professional masked animation for covert administration.\n"
    "- Advanced Screen Rotation: 90, 180, 270 degree hardware-level rotation.\n"
    "- Phishing & BSOD: Professional mock-ups for authorized security training."
)

pdf.chapter_title("4. SYSTEM DEEP-DIVE")
pdf.chapter_body(
    "- SHA256 Verification: Verify file integrity remotely via hardware-accelerated hashing.\n"
    "- Scheduled Task Manager: Audit and manage persistence and system maintenance tasks.\n"
    "- Audio/Visual Dominance: Remote volume and brightness control with precision sliders.\n"
    "- Event Log Sync: Real-time retrieval of the latest 50 system event records."
)

pdf.set_font('helvetica', 'B', 12)
pdf.set_text_color(255, 0, 0)
pdf.cell(0, 10, "STRICTLY FOR AUTHORIZED ADMINISTRATIVE USE ONLY.", ln=True, align='C')

output_path = os.path.join("RedMeFast", "README_GOD_MODE_v40.pdf")
if not os.path.exists("RedMeFast"): os.makedirs("RedMeFast")
pdf.output(output_path)
print(f"Documentation generated at {output_path}")
