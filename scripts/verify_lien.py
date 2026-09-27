import subprocess
import os

chrome = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
out_path = r'C:\Users\mdbaa\Downloads\SIH_Slide_Screenshots\test_modal_lien.png'

# We can trigger the modal using JavaScript or by clicking the button in the browser
# Let's verify in index.html and app.js that line 1818 now produces [OK] LIEN MARKED
with open('app/static/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

print('Contains [OK] LIEN MARKED:', '[OK] LIEN MARKED' in js)
print('Contains [OK] FROZEN:', '[OK] FROZEN' in js)
