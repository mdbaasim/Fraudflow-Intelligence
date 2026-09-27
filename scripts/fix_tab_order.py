with open('app/static/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

target = ''' window.addEventListener('DOMContentLoaded', async () => {
 initAuthSession();
 initMap();
 setupEventListeners();
 startSparkwaveEngine();
 await fetchCases();
 await updateBlockchainStatusBadge();
 const urlParams = new URLSearchParams(window.location.search);
 const targetTab = urlParams.get('tab') || window.location.hash.replace('#', '');
 if (targetTab) {
   setTimeout(() => switchTab(targetTab), 150);
 }
 });'''

replacement = ''' window.addEventListener('DOMContentLoaded', async () => {
 const urlParams = new URLSearchParams(window.location.search);
 const targetTab = urlParams.get('tab') || window.location.hash.replace('#', '');
 if (targetTab) {
   switchTab(targetTab);
 }
 initAuthSession();
 initMap();
 setupEventListeners();
 startSparkwaveEngine();
 await fetchCases();
 await updateBlockchainStatusBadge();
 if (targetTab) {
   switchTab(targetTab);
 }
 });'''

if target in js:
    js = js.replace(target, replacement)
    with open('app/static/app.js', 'w', encoding='utf-8') as f:
        f.write(js)
    print('Updated DOMContentLoaded order successfully!')
else:
    print('Target not matched in app.js')
