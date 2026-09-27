import re

with open('app/static/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

with open('app/static/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

html_ids = set(re.findall(r'id=["\']([a-zA-Z0-9\-_]+)["\']', html))
js_ids = set(re.findall(r'getElementById\(["\']([a-zA-Z0-9\-_]+)["\']\)', js))

missing = js_ids - html_ids
# Dynamic IDs created programmatically in app.js
missing.discard('btn-signout')
missing.discard('btn-wallet-freeze-action')
missing.discard('btn-download-crypto-notice')

print("Missing IDs:", missing)
print("Total JS IDs:", len(js_ids))
print("All JS IDs:", sorted(list(js_ids)))
if not missing:
    print("ALL DOM IDs match 100% between index.html and app.js!")
