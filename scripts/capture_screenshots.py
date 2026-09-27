import subprocess
import time
import json
import urllib.request
import websocket
import base64

chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
port = 9225

proc = subprocess.Popen([
    chrome_path,
    '--headless=new',
    f'--remote-debugging-port={port}',
    '--remote-allow-origins=*',
    '--disable-gpu',
    '--no-sandbox',
    '--window-size=1920,1080',
    'http://127.0.0.1:8001/'
])

time.sleep(3)
msg_counter = 1

def run_capture():
    global msg_counter
    try:
        with urllib.request.urlopen(f'http://127.0.0.1:{port}/json') as r:
            tabs = json.loads(r.read().decode())
        app_tab = next((t for t in tabs if '8001' in t.get('url', '')), tabs[0])
        ws = websocket.create_connection(app_tab['webSocketDebuggerUrl'], timeout=10)

        def send(method, params=None):
            global msg_counter
            ws.send(json.dumps({"id": msg_counter, "method": method, "params": params or {}}))
            msg_counter += 1

        def wait_resp():
            while True:
                raw = ws.recv()
                data = json.loads(raw)
                if data.get("id") == msg_counter - 1:
                    return data.get("result", {})

        send("Runtime.enable")
        wait_resp()
        send("Page.enable")
        wait_resp()

        # Helper to click tab and take screenshot
        def capture_view(tab_name, filename):
            # Click tab
            script = f"(() => {{ const b = document.querySelector('[data-tab=\"{tab_name}\"]'); if (b) b.click(); }})()"
            send("Runtime.evaluate", {"expression": script})
            wait_resp()
            time.sleep(2) # wait for map/graph render
            send("Page.captureScreenshot", {"format": "png"})
            res = wait_resp()
            img_b64 = res.get("data")
            if img_b64:
                with open(filename, "wb") as f:
                    f.write(base64.b64decode(img_b64))
                print(f"Saved: {filename}")

        # 1. Main Graph View (seed & simulate first)
        send("Runtime.evaluate", {"expression": "(() => { const b = document.getElementById('btn-simulate'); if(b) b.click(); })()"})
        wait_resp()
        time.sleep(2)
        capture_view("tab-graph", r"C:\Users\mdbaa\OneDrive\Desktop\SIH PRO\screenshot_1_graph_dashboard.png")

        # 2. ATM GIS Map View
        capture_view("tab-map", r"C:\Users\mdbaa\OneDrive\Desktop\SIH PRO\screenshot_2_atm_map.png")

        # 3. Court Dossier & Sec 102 View
        capture_view("tab-dossier", r"C:\Users\mdbaa\OneDrive\Desktop\SIH PRO\screenshot_3_court_dossier.png")

        ws.close()
    finally:
        proc.terminate()

run_capture()
