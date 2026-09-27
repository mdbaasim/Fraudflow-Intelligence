with open('app/static/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Find the end of app.js from "// App Bootstrap"
bootstrap_idx = js.rfind('// App Bootstrap')
if bootstrap_idx != -1:
    clean_js = js[:bootstrap_idx] + '''// App Bootstrap
  window.addEventListener('DOMContentLoaded', async () => {
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
  });

})();
'''
    with open('app/static/app.js', 'w', encoding='utf-8') as f:
        f.write(clean_js)
    print('Rewrote clean bootstrap block with proper closing brackets!')
else:
    print('// App Bootstrap not found')
