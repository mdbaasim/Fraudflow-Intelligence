import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
import re
from app.main import app

registered_routes = [r.path for r in app.routes if hasattr(r, 'path')]

with open('app/static/app.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

# Find all fetch calls
fetch_patterns = re.findall(r'fetch\([`\'"]([^`\'"?]+)', js_content)
print(f"Total fetch calls found: {len(fetch_patterns)}")
for fp in set(fetch_patterns):
    print("Found fetch:", fp)

# Check DOM element IDs referenced in app.js vs index.html
with open('app/static/index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

html_ids = set(re.findall(r'id=["\']([^"\']+)["\']', html_content))
js_ids = set(re.findall(r'getElementById\(["\']([^"\']+)["\']\)', js_content))

missing_ids = js_ids - html_ids
print("\nIDs in JS but missing in HTML:")
if missing_ids:
    for mid in sorted(missing_ids):
        print(f"  MISSING ID: {mid}")
else:
    print("  None! All getElementById references exist in HTML.")

# Check for event listeners or querySelector references
query_selectors = set(re.findall(r'querySelector(?:All)?\(["\']#([^"\'\s,>+~:]+)["\']\)', js_content))
missing_qs = query_selectors - html_ids
print("\nQuerySelectors (#id) missing in HTML:")
if missing_qs:
    for mid in sorted(missing_qs):
        print(f"  MISSING QS ID: {mid}")
else:
    print("  None! All querySelector IDs exist in HTML.")
