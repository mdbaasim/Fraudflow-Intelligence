import subprocess
import os
from PIL import Image

chrome = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
out_dir = r'C:\Users\mdbaa\Downloads\SIH_Slide_Screenshots'
os.makedirs(out_dir, exist_ok=True)

# 1. Capture Dashboard Overview
shot_dash = os.path.join(out_dir, '1_Prototype_Dashboard_Overview.png')
subprocess.run([
    chrome, '--headless', '--disable-gpu',
    '--window-size=1500,920', '--virtual-time-budget=3000',
    f'--screenshot={shot_dash}', 'http://127.0.0.1:8001/'
], capture_output=True, text=True)

# 2. Capture Transaction Flow Directed Graph
shot_tx = os.path.join(out_dir, 'Transaction_Network_Graph.png')
subprocess.run([
    chrome, '--headless', '--disable-gpu',
    '--window-size=1500,920', '--virtual-time-budget=3500',
    f'--screenshot={shot_tx}', 'http://127.0.0.1:8001/?tab=tx-flow'
], capture_output=True, text=True)

# 3. Capture Section 65B Blockchain Report
shot_rep = os.path.join(out_dir, '4_System_Status_Blockchain_Ledger.png')
subprocess.run([
    chrome, '--headless', '--disable-gpu',
    '--window-size=1500,920', '--virtual-time-budget=3500',
    f'--screenshot={shot_rep}', 'http://127.0.0.1:8001/?tab=reports'
], capture_output=True, text=True)

# 4. Capture Tactical ATM Cashout Map
shot_map = os.path.join(out_dir, 'CashOut_Map_Radar.png')
subprocess.run([
    chrome, '--headless', '--disable-gpu',
    '--window-size=1500,920', '--virtual-time-budget=3500',
    f'--screenshot={shot_map}', 'http://127.0.0.1:8001/?tab=map-cashout'
], capture_output=True, text=True)

# Generate tailored crops for each of the 5 slide boxes
img_dash = Image.open(shot_dash)
img_tx = Image.open(shot_tx)
img_rep = Image.open(shot_rep)
img_map = Image.open(shot_map)

# Box 1: Left Command Center (with Golden Hour + Authorize Sec 102 Freeze)
img_dash.crop((10, 190, 980, 920)).save(os.path.join(out_dir, 'Box_1_Command_Center_Crop.png'))

# Box 2: Live Ingestion Stream & Incident Audit Trail
img_dash.crop((280, 600, 1480, 915)).save(os.path.join(out_dir, 'Box_2_Live_Data_Ingestion.png'))

# Box 3: Forensic Risk Score & Glowing Harmonic Wave Curve (845 / 850)
img_dash.crop((280, 270, 1480, 590)).save(os.path.join(out_dir, 'Box_3_Alerts_Trends_Wave.png'))

# Box 4: Official Police Case Dossier & Section 65B Evidence Report
img_rep.crop((280, 200, 1480, 910)).save(os.path.join(out_dir, 'Box_4_System_Status_Blockchain.png'))

# Box 5: Multi-Hop Directed Topology Graph (Victim -> Mules -> Cashout)
img_tx.crop((280, 190, 1480, 830)).save(os.path.join(out_dir, 'Box_5_Scalability_Mule_Graph.png'))

# Box 5 Alternative: ATM Radar Map
img_map.crop((280, 190, 1480, 890)).save(os.path.join(out_dir, 'Box_5_Alternative_ATM_Radar_Map.png'))

print('All 5 slide images successfully captured and cropped!')
