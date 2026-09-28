import re

def clean_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove elements entry
    content = content.replace("  btnFreezeMessageBanks: document.getElementById('btn-freeze-message-banks'),\n", "")
    content = content.replace(" btnFreezeMessageBanks: document.getElementById('btn-freeze-message-banks'),\n", "")

    # Remove listeners
    pat = r"if\s*\(\s*elements\.btnFreezeMessageBanks\s*\)[\s\S]*?directFreezeBtn\.addEventListener\('click',\s*triggerGoldenHourFreezeBlast\);\s*\}"
    content = re.sub(pat, "", content)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Cleaned {path}")

clean_file('public/app.js')
clean_file('app/static/app.js')
