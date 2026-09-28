import os

def update_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add element to elements object
    old_elem = " counterFundsSaved: document.getElementById('counter-funds-saved'),\n btnEmergencyFreezeBlast: document.getElementById('btn-emergency-freeze-blast'),"
    new_elem = " counterFundsSaved: document.getElementById('counter-funds-saved'),\n btnFreezeMessageBanks: document.getElementById('btn-freeze-message-banks'),\n btnEmergencyFreezeBlast: document.getElementById('btn-emergency-freeze-blast'),"
    if old_elem in content:
        content = content.replace(old_elem, new_elem, 1)
        print(f"Updated elements object in {path}")
    else:
        print(f"elements object pattern not found in {path}")

    # 2. Add event listener
    old_listener = "  if (elements.btnEmergencyFreezeBlast) {\n    elements.btnEmergencyFreezeBlast.addEventListener('click', triggerGoldenHourFreezeBlast);\n  }"
    new_listener = """  if (elements.btnFreezeMessageBanks) {
    elements.btnFreezeMessageBanks.addEventListener('click', triggerGoldenHourFreezeBlast);
  }
  const directFreezeBtn = document.getElementById('btn-freeze-message-banks');
  if (directFreezeBtn) {
    directFreezeBtn.addEventListener('click', triggerGoldenHourFreezeBlast);
  }
  if (elements.btnEmergencyFreezeBlast) {
    elements.btnEmergencyFreezeBlast.addEventListener('click', triggerGoldenHourFreezeBlast);
  }"""
    if old_listener in content:
        content = content.replace(old_listener, new_listener, 1)
        print(f"Updated listener in {path}")
    else:
        # Try alternate whitespace
        import re
        pat = r"if\s*\(\s*elements\.btnEmergencyFreezeBlast\s*\)\s*\{\s*elements\.btnEmergencyFreezeBlast\.addEventListener\('click',\s*triggerGoldenHourFreezeBlast\);\s*\}"
        if re.search(pat, content):
            content = re.sub(pat, new_listener, content, count=1)
            print(f"Regex replaced listener in {path}")
        else:
            print(f"Listener pattern not found in {path}")

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

update_file('public/app.js')
update_file('app/static/app.js')
print("Done updating app.js files.")
