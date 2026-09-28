import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

doc = docx.Document()

# Page Margins
for section in doc.sections:
    section.top_margin = Inches(0.8)
    section.bottom_margin = Inches(0.8)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)

def set_cell_background(cell, fill_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

# Title
title = doc.add_heading('SMART INDIA HACKATHON — OFFICIAL 3-MINUTE YOUTUBE VOICEOVER SCRIPT', level=0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

# Metadata
p_meta = doc.add_paragraph()
r_meta = p_meta.add_run('Project Name: ')
r_meta.bold = True
p_meta.add_run('FraudFlow Intelligence\n')
r_meta2 = p_meta.add_run('Problem Statement ID: ')
r_meta2.bold = True
p_meta.add_run('SIH26184 — Multi-Hop Financial Cyber Fraud Interception & Decision Support\n')
r_meta3 = p_meta.add_run('Target Voiceover Duration: ')
r_meta3.bold = True
p_meta.add_run('3 Minutes (Paced for 130 words per minute in simple, clear English)\n')
r_meta4 = p_meta.add_run('Purpose: ')
r_meta4.bold = True
p_meta.add_run('Read this script word-for-word while recording your screen.')

doc.add_heading('VOICEOVER SCRIPT (TIMED WITH SCREEN ACTIONS)', level=1)

script_sections = [
    (
        "0:00 - 0:30 | The Problem Hook and System Introduction",
        "Screen Action: Show the full FraudFlow dashboard on your screen.",
        "\"Hello judges and viewers. Every day in India, innocent citizens lose their hard-earned money to cyber fraud. Once stolen, criminals quickly transfer this money across multiple bank accounts in just fifteen minutes and withdraw it from ATMs before the police can even react.\n\nTraditional police notices take two to three days. By that time, the money is gone. To solve this critical national challenge, we built FraudFlow—an automated AI tactical system that traces money trails in real-time, predicts where criminals will withdraw cash, and freezes accounts in seconds.\""
    ),
    (
        "0:30 - 1:00 | Left Control Panel & Sidebar Controls",
        "Screen Action: Point to the Left Sidebar, show input boxes, click '+ New Case', and select a case from the Case Docket dropdown.",
        "\"Let us look at the Left Control Panel.\n\nHere, an investigating officer can manage case dockets and input live complaints: the Complaint Number, the Victim Name, the Initial Loss Amount, and the Incident City. Our software works dynamically for ANY Indian city and ANY bank.\n\nNow look at the controls on this panel:\n• First, the '+ New Case' button at the top right of Case Details: Clicking this clears all input boxes so you can enter a completely fresh complaint.\n• Second, the primary action button labeled 'Execute Flow Analysis & Forecast' (or 'Save & Trace Fraud'): When clicked, our graph engine reads the input and reconstructs the money flow.\n• Third, the Case Docket dropdown at the top: Selecting our demo case—such as A. Murugesan from Dindigul—instantly loads a live multi-hop fraud scenario across multiple banks for live demonstration.\""
    ),
    (
        "1:00 - 1:40 | The Money Trail Graph & Tactical Buttons",
        "Screen Action: Switch to the Transaction Trail tab. Click 'Filter Critical Path', zoom, and click an account node.",
        "\"Look at the main screen. This is our Transaction Trail Graph.\n\nNode 0 on the left is the Victim. Moving right, Hops 1, 2, 3, and 4 trace the mule accounts across different banks, all the way to Layer 5 where the money is about to be cashed out.\n\nNow look at the graph control buttons at the top:\n• 'Fit View' button: Automatically fits the entire graph on your screen.\n• 'Zoom In' and 'Zoom Out' buttons: Allow you to inspect large networks with over fifty accounts.\n• 'Filter Critical Path' button: When I click this button, the system removes background noise and highlights the main channel where eighty percent of the stolen money is escaping.\n• Node Inspection: When I click on any bank node, an inspector window pops up showing the Bank IFSC, Branch, Account Holder Name, and Aadhaar verification status.\""
    ),
    (
        "1:40 - 2:20 | Navigation Menu & Predictive ATM Map",
        "Screen Action: Click the Hamburger Menu [ ☰ ], then click the 'ATM Spatial Hotspots' tab.",
        "\"Now let us click the Hamburger Menu [ ☰ ] at the top left. This opens our complete navigation drawer with all six operational modules.\n\nLet us click the second tab: 'ATM Spatial Hotspots'.\n\nThis opens our interactive GIS map. The green pin marks where the victim was scammed. The red pulsing rings show our AI prediction: based on travel speed, withdrawal history, and ATM cash limits, FraudFlow predicts the top three ATM kiosks where the criminal is heading to withdraw cash within the next twenty minutes. Police patrol teams can be dispatched directly to these ATMs to catch the mules red-handed.\""
    ),
    (
        "2:20 - 3:00 | Automated Freezing & Court Evidence Dossier",
        "Screen Action: Click 'Regulatory Notice' tab, click 'Generate Freeze Order', then click 'Court Evidence Dossier' tab.",
        "\"Next, let us click the 'Regulatory Notice' tab.\n\nHere you see the 'Generate Freeze Order' button. When clicked, FraudFlow instantly generates a legally binding freeze directive under Section 102 CrPC and Section 106 Bharatiya Nagarik Suraksha Sanhita. When connected to banking gateways, this stops debit transactions in real-time before money leaves the bank.\n\nFinally, let us click the 'Court Evidence Dossier' tab.\n\nHere you see the 'Export Forensic Dossier' button. This compiles a complete digital evidence report secured with a cryptographic SHA-256 blockchain hash. This makes the evidence fully admissible in court under Section 65B of the Indian Evidence Act.\""
    ),
    (
        "3:00 - 3:15 | Powerful Closing",
        "Screen Action: Return to the main dashboard view.",
        "\"In conclusion, FraudFlow transforms days of slow paperwork into a fifteen-second automated intervention—protecting citizens and saving public money.\n\nThank you, Smart India Hackathon jury. Jai Hind!\""
    )
]

for time_header, cue, spoken in script_sections:
    h = doc.add_heading(time_header, level=2)
    p_cue = doc.add_paragraph()
    r_cue = p_cue.add_run(cue)
    r_cue.italic = True
    r_cue.font.color.rgb = RGBColor(0, 102, 204)
    p_spoken = doc.add_paragraph()
    r_spoken = p_spoken.add_run(spoken)
    r_spoken.font.size = Pt(11)

doc.add_page_break()

# Button-by-Button Explanation Table
doc.add_heading('BUTTON-BY-BUTTON EXPLANATION REFERENCE TABLE', level=1)
doc.add_paragraph('Here is the quick-reference cheat sheet explaining every single button in simple terms:')

btn_headers = ['Button Name', 'Where It Is', 'Simple 1-Line Explanation to Speak']
btn_data = [
    ('Hamburger [ ☰ ]', 'Top Left Header', 'Opens the navigation drawer to switch between all six tactical views.'),
    ('Case Docket Dropdown', 'Top of Left Sidebar', 'Selecting any case (e.g. A. Murugesan - Dindigul) loads the live multi-hop fraud scenario for demonstration.'),
    ('Execute Flow Analysis & Forecast', 'Left Sidebar (Big Button)', 'Runs our graph algorithm and reconstructs the money flow across all mule accounts.'),
    ('+ New Case', 'Top Right of Case Details', 'Clears all input boxes so you can enter a completely new victim complaint.'),
    ('Save & Trace Fraud', 'Bottom of Case Details', 'Saves the custom complaint inputs and traces the money flow.'),
    ('Transaction Trail Tab', 'Main Tabs / Drawer', 'Displays the visual money flow from victim to layer 5 mule bank accounts.'),
    ('Filter Critical Path', 'Above the Graph', 'Removes small transactions and highlights the main channel where stolen money is escaping.'),
    ('Fit View', 'Above the Graph', 'Centers and scales the graph so the entire money trail fits on screen.'),
    ('Account Node (Clicking any node)', 'Inside the Graph', 'Pops up detailed account info: Bank IFSC, account status, and transaction time.'),
    ('ATM Spatial Hotspots Tab', 'Main Tabs / Drawer', 'Shows the GIS map with red rings predicting which ATMs fraudsters will use next.'),
    ('Mule Network Analytics Tab', 'Main Tabs / Drawer', 'Displays syndicate clusters, shared mobile numbers, and linked device IMEIs.'),
    ('Interception Feed Tab', 'Main Tabs / Drawer', 'Shows real-time status of automated freeze orders sent to partner banks.'),
    ('Regulatory Notice Tab', 'Main Tabs / Drawer', 'Creates legal bank freeze notices under Section 102 CrPC and Section 106 BNSS.'),
    ('Generate Freeze Order', 'Inside Regulatory Notice', 'Automatically writes the official legal freeze order addressed to the bank manager.'),
    ('Court Evidence Dossier Tab', 'Main Tabs / Drawer', 'Generates the official court report secured with a SHA-256 digital fingerprint.'),
    ('Export Forensic Dossier', 'Inside Court Dossier', 'Downloads the tamper-proof evidence package ready for court under Section 65B.')
]

table = doc.add_table(rows=len(btn_data) + 1, cols=3)
table.style = 'Table Grid'
table.alignment = WD_TABLE_ALIGNMENT.CENTER

for col_idx, h_text in enumerate(btn_headers):
    cell = table.cell(0, col_idx)
    cell.text = h_text
    set_cell_background(cell, "1F497D")
    for p in cell.paragraphs:
        for r in p.runs:
            r.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255)
            r.font.size = Pt(10)

for row_idx, row_vals in enumerate(btn_data):
    for col_idx, val in enumerate(row_vals):
        cell = table.cell(row_idx + 1, col_idx)
        cell.text = val
        for p in cell.paragraphs:
            for r in p.runs:
                r.font.size = Pt(9.5)

output_file = r'C:\Users\mdbaa\OneDrive\Desktop\SIH PRO\SIH_Prototype_Voiceover_Script.docx'
doc.save(output_file)
print(f'Voiceover docx generated successfully at: {output_file}')
