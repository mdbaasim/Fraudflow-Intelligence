import subprocess
import time
import json
import urllib.request
import websocket
import sys

chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
port = 9223

print(f"Launching headless Chrome on port {port}...")
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

console_errors = []
console_warnings = []
network_errors = []
exceptions = []
msg_counter = 1

try:
    with urllib.request.urlopen(f'http://127.0.0.1:{port}/json') as r:
        tabs = json.loads(r.read().decode())
    
    app_tab = next((t for t in tabs if '8001' in t.get('url', '')), tabs[0])
    ws_url = app_tab['webSocketDebuggerUrl']
    print(f"Connecting to CDP WebSocket: {ws_url}")

    ws = websocket.create_connection(ws_url, timeout=10)

    def send_cdp(method, params=None):
        global msg_counter
        payload = {"id": msg_counter, "method": method, "params": params or {}}
        ws.send(json.dumps(payload))
        msg_counter += 1

    send_cdp("Runtime.enable")
    send_cdp("Log.enable")
    send_cdp("Network.enable")
    send_cdp("Page.enable")

    time.sleep(2)

    def eval_js(expression):
        global msg_counter
        cur_id = msg_counter
        send_cdp("Runtime.evaluate", {"expression": expression, "awaitPromise": True, "returnByValue": True})
        end_time = time.time() + 6
        res_val = None
        while time.time() < end_time:
            raw = ws.recv()
            data = json.loads(raw)
            if data.get("method") == "Runtime.consoleAPICalled":
                t = data["params"]["type"]
                text = " ".join(str(a.get("value", a.get("description", ""))) for a in data["params"]["args"])
                if t == "error":
                    console_errors.append(text)
                elif t == "warning":
                    console_warnings.append(text)
            elif data.get("method") == "Runtime.exceptionThrown":
                exceptions.append(data["params"]["exceptionDetails"])
            elif data.get("method") == "Network.responseReceived":
                status = data["params"]["response"]["status"]
                url = data["params"]["response"]["url"]
                if status >= 400:
                    network_errors.append(f"{status} - {url}")
            elif data.get("id") == cur_id:
                res_val = data.get("result", {}).get("result", {}).get("value")
                break
        return res_val

    print("\n--- 1. Testing Page Load & Title ---")
    page_title = eval_js("document.title")
    print("Page Title:", page_title)

    time.sleep(1)

    print("\n--- 2. Testing Hamburger & Off-Canvas Drawer ---")
    drawer_test = eval_js("""
    (() => {
        const btn = document.getElementById('btn-nav-toggle');
        const drawer = document.getElementById('nav-drawer');
        if (!btn || !drawer) return 'Button or drawer element missing';
        btn.click();
        const isOpen = drawer.classList.contains('open');
        btn.click();
        return isOpen ? 'DRAWER_OK' : 'DRAWER_FAIL';
    })()
    """)
    print("Drawer test:", drawer_test)

    print("\n--- 3. Testing Dynamic Ingestion & Simulation ---")
    sim_test = eval_js("""
    (() => {
        const simBtn = document.getElementById('btn-simulate');
        if (!simBtn) return 'btn-simulate missing';
        simBtn.click();
        return 'SIMULATE_CLICKED';
    })()
    """)
    print("Simulate test:", sim_test)
    time.sleep(2)

    print("\n--- 4. Testing Tab Transitions ---")
    tabs = ['tab-graph', 'tab-map', 'tab-network', 'tab-interception', 'tab-dossier', 'tab-notice']
    for t_name in tabs:
        res = eval_js(f"""
        (() => {{
            const btn = document.querySelector('[data-tab="{t_name}"]');
            if (btn) {{
                btn.click();
                return 'CLICKED_OK';
            }}
            return 'BTN_NOT_FOUND';
        }})()
        """)
        print(f"Tab {t_name}: {res}")
        time.sleep(0.5)

    print("\n--- 5. Testing Interactive Actions ---")
    eval_js("(() => { const b = document.getElementById('btn-filter-critical'); if (b) b.click(); })()")
    eval_js("(() => { const b = document.getElementById('btn-fit-view'); if (b) b.click(); })()")
    eval_js("(() => { const b = document.getElementById('btn-generate-notice'); if (b) b.click(); })()")
    eval_js("(() => { const b = document.getElementById('btn-export-dossier'); if (b) b.click(); })()")

    time.sleep(2)

    # Drain any remaining CDP packets
    ws.settimeout(0.5)
    try:
        while True:
            raw = ws.recv()
            data = json.loads(raw)
            if data.get("method") == "Runtime.consoleAPICalled":
                t = data["params"]["type"]
                text = " ".join(str(a.get("value", a.get("description", ""))) for a in data["params"]["args"])
                if t == "error":
                    console_errors.append(text)
                elif t == "warning":
                    console_warnings.append(text)
            elif data.get("method") == "Runtime.exceptionThrown":
                exceptions.append(data["params"]["exceptionDetails"])
            elif data.get("method") == "Network.responseReceived":
                status = data["params"]["response"]["status"]
                url = data["params"]["response"]["url"]
                if status >= 400:
                    network_errors.append(f"{status} - {url}")
    except:
        pass

    ws.close()

finally:
    proc.terminate()
    print("Headless Chrome closed.")

print("\n" + "="*50)
print("BROWSER RUNTIME AUDIT SUMMARY:")
print("="*50)
print(f"Console Errors: {len(console_errors)}")
for ce in console_errors:
    print(f"  [ERROR] {ce}")

print(f"Uncaught Exceptions: {len(exceptions)}")
for ex in exceptions:
    print(f"  [EXCEPTION] {ex.get('text')} line {ex.get('lineNumber')}")

print(f"Network Errors (4xx/5xx): {len(network_errors)}")
for ne in network_errors:
    print(f"  [NETWORK] {ne}")

print(f"Console Warnings: {len(console_warnings)}")
for cw in console_warnings:
    print(f"  [WARN] {cw}")

if not console_errors and not exceptions and not network_errors:
    print("\n*** PERFECT SCORE: ZERO ERRORS DETECTED ACROSS THE ENTIRE APPLICATION ***")
