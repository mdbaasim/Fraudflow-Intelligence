with open('app/static/app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "const initialHash = window.location.hash.replace('#', '');" in line:
        new_lines.append(" const urlParams = new URLSearchParams(window.location.search);\n")
        new_lines.append(" const targetTab = urlParams.get('tab') || window.location.hash.replace('#', '');\n")
        new_lines.append(" if (targetTab) {\n")
        new_lines.append("   setTimeout(() => switchTab(targetTab), 150);\n")
        new_lines.append(" }\n")
    elif "if (initialHash) {" in line or "setTimeout(() => switchTab(initialHash), 300);" in line or ("}" in line and len(new_lines) > 0 and "switchTab(targetTab)" in new_lines[-2]):
        continue
    else:
        new_lines.append(line)

with open('app/static/app.js', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('Tab search parameter logic updated successfully')
