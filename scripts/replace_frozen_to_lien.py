# Update app.js
with open('app/static/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

js = js.replace("[OK] FROZEN (", "[OK] LIEN MARKED (")
js = js.replace("Section 102 Debit Freeze", "Section 102 Statutory Lien")
js = js.replace("mark an emergency lien / debit freeze", "mark an emergency statutory lien")
js = js.replace("Immediate Section 91 CrPC freeze directive", "Immediate Section 102 CrPC lien directive")
js = js.replace("Failed to mint on-chain freeze directive", "Failed to mint on-chain lien directive")
js = js.replace("Freeze Directive ", "Lien Directive ")

with open('app/static/app.js', 'w', encoding='utf-8') as f:
    f.write(js)
print('app.js updated: [OK] FROZEN -> [OK] LIEN MARKED')

# Update index.html
with open('app/static/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace("[OK] Section 102 Debit Freeze", "[OK] Section 102 Statutory Lien")
html = html.replace("Freeze Directive Ready", "Lien Directive Ready")
html = html.replace("Funds Successfully Frozen in Digital Transit", "Funds Successfully Lien-Marked in Transit")
html = html.replace("Issue On-Chain Freeze Directive (CrPC 91)", "Issue On-Chain Lien Directive (CrPC 91/102)")
html = html.replace("Issue On-Chain Inter-Bank Freeze Directive", "Issue On-Chain Inter-Bank Lien Directive")
html = html.replace("Statutory Freeze Amount (INR)", "Statutory Lien Amount (INR)")

# Bump cache buster
html = html.replace("styles.css?v=2.1.1", "styles.css?v=2.1.2")
html = html.replace("app.js?v=2.1.1", "app.js?v=2.1.2")

with open('app/static/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('index.html updated successfully!')
