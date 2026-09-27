import subprocess
import os

chrome = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
out_path = r'C:\Users\mdbaa\Downloads\SIH_Slide_Screenshots\verified_modal_lien.png'

# We can launch Chrome with a tiny script evaluation to trigger the button
# Or navigate to a test page that triggers triggerGoldenHourFreezeBlast()
test_html = '''<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body>
<script>
window.location.href = "http://127.0.0.1:8001/";
</script>
</body>
</html>'''

cmd = [
    chrome, '--headless', '--disable-gpu',
    '--window-size=1200,900', '--virtual-time-budget=3500',
    f'--screenshot={out_path}',
    'http://127.0.0.1:8001/'
]
subprocess.run(cmd, capture_output=True, text=True)
print('Screenshot taken!')
