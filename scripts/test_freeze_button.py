import subprocess
import time
import json
import urllib.request
import websocket

chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
port = 9226

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

try:
    with urllib.request.urlopen(f'http://127.0.0.1:{port}/json') as r:
        tabs = json.loads(r.read().decode())
    
    app_tab = next((t for t in tabs if '8001' in t.get('url', '')), tabs[0])
    ws = websocket.create_connection(app_tab['webSocketDebuggerUrl'], timeout=10)

    msg_id = 1
    def send(method, params=None):
        global msg_id
        ws.send(json.dumps({"id": msg_id, "method": method, "params": params or {}}))
        msg_id += 1

    send("Runtime.enable")
    time.sleep(1)

    # Click the new Freeze Accounts & Send Message to Banks button
    script = """
    (() => {
        const btn = document.getElementById('btn-freeze-message-banks');
        if (!btn) return 'BUTTON_NOT_FOUND';
        btn.click();
        const modal = document.getElementById('modal-freeze-blast');
        const isOpen = modal && modal.classList.contains('active');
        return isOpen ? 'FREEZE_MODAL_OPENED_SUCCESSFULLY' : 'MODAL_NOT_OPEN';
    })()
    """
    send("Runtime.evaluate", {"expression": script, "returnByValue": True})
    
    end_time = time.time() + 4
    result = None
    while time.time() < end_time:
        raw = ws.recv()
        d = json.loads(raw)
        if d.get("id") == msg_id - 1:
            result = d.get("result", {}).get("result", {}).get("value")
            break

    print("Test Result for Freeze Message Button:", result)
    ws.close()
finally:
    proc.terminate()
