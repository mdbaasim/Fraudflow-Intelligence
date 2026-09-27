import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

doc = docx.Document()

# Page Margins
for section in doc.sections:
    section.top_margin = Inches(0.8)
    section.bottom_margin = Inches(0.8)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)

# Title
title = doc.add_heading('SMART INDIA HACKATHON (SIH) - WINNING 3-MINUTE YOUTUBE PITCH SCRIPT', level=0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

# Metadata box
p_meta = doc.add_paragraph()
p_meta.add_run('Problem Statement ID: ').bold = True
p_meta.add_run('SIH26184\n')
p_meta.add_run('Project Title: ').bold = True
p_meta.add_run('FraudFlow - Multi-Hop Financial Cyber Fraud Interception & Predictive Cash-Out Decision Support System\n')
p_meta.add_run('Target Duration: ').bold = True
p_meta.add_run('2 Minutes 45 Seconds - 3 Minutes\n')
p_meta.add_run('Target Audience: ').bold = True
p_meta.add_run('SIH Jury, Ministry of Home Affairs (I4C), Law Enforcement Agencies (LEAs), and Cyber Crime Units')

doc.add_heading('1. Recording Setup & Test Inputs', level=1)
p_setup = doc.add_paragraph()
p_setup.add_run('• Application URL: http://127.0.0.1:8001/\n')
p_setup.add_run('• Display: Full HD (1920x1080), Clean Browser Fullscreen (F11)\n')
p_setup.add_run('• Demo Complaint Number: NCRP-2024-8842\n')
p_setup.add_run('• Demo Complainant: Rajesh Sharma\n')
p_setup.add_run('• Demo Loss Amount: ₹ 2,50,000\n')
p_setup.add_run('• Demo Incident City: Bengaluru')

doc.add_heading('2. Timed Pitch Script with Video Actions', level=1)

sections_data = [
    ('[0:00 - 0:25] The Problem & System Hook',
     '[Video Action: Camera on speaker or full-screen view of the FraudFlow Dashboard]',
     'In India today, over 10,000 cyber financial fraud complaints are filed daily on the National Cyber Crime Reporting Portal (NCRP). Once a victim loses money, criminal syndicates execute multi-hop layering through mule accounts and cryptocurrency bridges in under 15 minutes, cashing out via ATMs before police can react.\n\nTraditional policing relies on manual notices under Section 91 CrPC, which takes days. We present FraudFlow—an AI-driven, automated tactical interception system that reconstructs money trails in real-time, predicts ATM cash-out vectors, and freezes accounts instantly under Section 102 CrPC and Section 106 Bharatiya Nagarik Suraksha Sanhita (BNSS).'),
    
    ('[0:25 - 0:50] Dynamic Ingestion & Immediate Graph Reconstruction',
     '[Video Action: Click left sidebar. Show inputs: Complaint No, Name, Amount, City. Click "Analyze Complaint Trail".]',
     'Let us demonstrate with a live complaint. In the Left Control Panel, an investigator enters any complaint details—regardless of the amount, name, or city. We hit "Analyze Complaint Trail".\n\nImmediately, our Graph Reconstruction Engine parses the complaint and builds a multi-tier Directed Acyclic Graph (DAG). Here on the screen:\n• Node 0 represents the Victim.\n• Hop 1 to Hop 4 trace the mule accounts across multiple banks.\n• Layer 5 isolates the final cash-out staging points.\n\nNotice the colored risk badges: Red for Critical, Amber for High. The system highlights the highest velocity laundering path using Dijkstra\'s shortest bottleneck algorithm.'),

    ('[0:50 - 1:20] Software Navigation & Module Overview',
     '[Video Action: Click the hamburger button [ ☰ ] to reveal the Navigation Drawer, then cycle cleanly through each module tab.]',
     'Clicking the Hamburger Menu [ ☰ ] at the top left opens our complete suite of 6 operational modules:\n\n1. Transaction Trail (Graph Visualizer): Interactive inspection showing Bank IFSC, Mule Account Holder, Risk Score, and Inflow-Outflow balance.\n2. ATM Spatial Hotspots (GIS Map): Powered by Leaflet GIS, our AI analyzes historical withdrawal velocity and geo-predicts the top 3 ATM kiosks where the fraudster is heading to withdraw cash within the next 20 minutes.\n3. Mule Network Analytics: Identifies shared digital fingerprints—duplicate phone numbers, device IMEIs, and KYC collusion clusters across syndicates.\n4. Interception Feed: Displays live telemetric status of automated freeze orders dispatched to partner bank APIs.\n5. Court Evidence Dossier: Generates tamper-proof PDF forensic reports complete with cryptographic SHA-256 digital hash verification, ready for submission to court under Section 65B of the Indian Evidence Act.\n6. Regulatory Section 102 Notice: Instantly creates automated, legally binding account freezing notices complying with RBI circulars and legal mandates.'),

    ('[1:20 - 1:55] Tactical Features: Graph Controls & Filters',
     '[Video Action: Switch to the Transaction Trail tab. Click "Filter Critical Path", zoom the graph, and click an account node to show the modal.]',
     'Let us look at the operational controls right above the graph:\n• Filter Critical Path: Instantly eliminates noise and isolates only the high-risk laundering channel where 80% of the funds are escaping.\n• Fit View & Reset Zoom: Allows investigators to focus on complex networks with over 50 hops.\n• Node Inspection: When I click on Mule Account-3, the Inspector Panel opens with complete provenance: account status, Aadhaar linked state, and transaction timestamps down to the millisecond.'),

    ('[1:55 - 2:25] Predictive Cash-Out & Automated Bank Freezing',
     '[Video Action: Switch to the ATM Spatial Hotspots tab, then switch to the Regulatory Notice tab and click "Generate Sec 102 CrPC Freeze Order".]',
     'Now look at the ATM Spatial Hotspots tab. Notice the green pin—that is the incident origin in Bengaluru. The red pulsing rings represent the predicted cash-out ATMs within a 3-kilometer radius, ranked by cash liquidity and CCTV coverage. Patrol units can be dispatched to these exact locations immediately.\n\nNext, we go to the Regulatory Notice tab and click "Generate Notice". In less than two seconds, FraudFlow generates an official Section 102 CrPC / Section 106 BNSS legal directive. When connected to the NPCI and core banking gateways, this triggers a real-time lien marker on the beneficiary accounts, stopping the cash leakage before the mule reaches the ATM counter.'),

    ('[2:25 - 2:55] Technical Architecture & SIH Winning Differentiators',
     '[Video Action: Show Court Evidence Dossier tab, click "Export Forensic Dossier", and show the SHA-256 Hash badge.]',
     'What makes FraudFlow unique and award-worthy:\n1. Universal Real-Time Ingestion: Works on ANY input, any bank, and any city across India without hardcoded limits.\n2. Predictive GIS Engine: While other solutions only track past transactions, FraudFlow predicts future cash-out locations.\n3. Chain of Custody: Every audit log and evidentiary report is hashed with SHA-256, ensuring strict compliance with Section 65B of the Indian Evidence Act.\n4. Lightweight & Cloud-Ready: Built on FastAPI, async event loops, and responsive frontend architecture that functions flawlessly on any law enforcement workstation or tablet.'),

    ('[2:55 - 3:10] Conclusion & Closing Impact',
     '[Video Action: Return to the Main Dashboard Overview]',
     'FraudFlow converts days of tedious paperwork into a 15-second tactical intervention—saving public funds and empowering Indian law enforcement.\n\nThank you, Smart India Hackathon jury. Jai Hind!')
]

for heading, cue, speech in sections_data:
    h = doc.add_heading(heading, level=2)
    p_cue = doc.add_paragraph()
    r_cue = p_cue.add_run(cue)
    r_cue.italic = True
    r_cue.font.color.rgb = RGBColor(0, 102, 204)
    p_speech = doc.add_paragraph()
    p_speech.add_run(speech)

doc.add_heading('3. Button-by-Button Reference Guide', level=1)

table_data = [
    ('Button / Control', 'Location', 'Exact Function & What to Say'),
    ('Hamburger [ ☰ ]', 'Top Navigation Bar (Left)', 'Opens the primary navigation drawer to switch between all 6 operational views.'),
    ('Analyze Complaint Trail', 'Left Sidebar Panel', 'Ingests the dynamic complaint details, executes the layering graph algorithm, and renders the multi-hop money flow.'),
    ('Simulate Multi-Hop Incident', 'Left Sidebar Panel', 'Instantly loads an active live scenario for rapid presentation and demonstration.'),
    ('Reset Form', 'Left Sidebar Panel', 'Clears all dynamic input fields so you can test any custom complaint.'),
    ('Transaction Trail Tab', 'Main Tabs / Drawer', 'Displays the interactive D3/SVG Directed Acyclic Graph tracing funds from victim to layer 5 mules.'),
    ('ATM Spatial Hotspots Tab', 'Main Tabs / Drawer', 'Opens Leaflet GIS map with velocity-based predictive ATM cash-out heat rings.'),
    ('Mule Network Analytics Tab', 'Main Tabs / Drawer', 'Shows syndicate clusters, shared device IMEI/phone patterns, and high-risk mule rings.'),
    ('Interception Feed Tab', 'Main Tabs / Drawer', 'Live streaming telemetric log of automated API calls made to partner bank core gateways.'),
    ('Court Evidence Dossier Tab', 'Main Tabs / Drawer', 'Compiles the official forensic audit trail with SHA-256 cryptographic verification.'),
    ('Regulatory Notice Tab', 'Main Tabs / Drawer', 'Formats statutory freezing orders under Section 102 CrPC and Section 106 BNSS.'),
    ('Filter Critical Path', 'Graph Header Bar', 'Filters out low-value transactions, highlighting the main laundering trunk.'),
    ('Fit View / Reset', 'Graph Header Bar', 'Re-centers and auto-scales the multi-tier graph to fit the viewport.'),
    ('Node Click (Any Account)', 'Inside Graph View', 'Opens the granular Account Details Modal (IFSC, Branch, Hold Status, KYC Flag).'),
    ('Generate Freeze Order', 'Regulatory Notice Tab', 'Auto-generates the legal freezing mandate addressed to the nodal bank officer.'),
    ('Export Dossier / Print', 'Court Dossier Tab', 'Produces a clean, print-ready Section 65B compliant legal evidentiary packet.')
]

table = doc.add_table(rows=len(table_data), cols=3)
table.alignment = WD_TABLE_ALIGNMENT.CENTER
table.style = 'Table Grid'

for i, row in enumerate(table_data):
    for j, val in enumerate(row):
        cell = table.cell(i, j)
        cell.text = val
        if i == 0:
            for p in cell.paragraphs:
                for r in p.runs:
                    r.bold = True
                    r.font.color.rgb = RGBColor(255, 255, 255)
            from docx.oxml import parse_xml
            from docx.oxml.ns import nsdecls
            shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="1F497D"/>')
            cell._tc.get_or_add_tcPr().append(shading_elm)

output_path = r'C:\Users\mdbaa\OneDrive\Desktop\SIH PRO\SIH_Presentation_Pitch_Script.docx'
doc.save(output_path)
print('DOCX successfully saved at:', output_path)
