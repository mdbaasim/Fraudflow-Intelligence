import re

with open('app/static/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update Header Brand Section to Official Government / MHA / I4C style
old_brand_title = re.search(r'<div class="brand-titles">.*?</div>\s*</div>\s*</div>', html, re.DOTALL)
if old_brand_title:
    new_brand_title = '''<div class="brand-titles">
          <div style="display: flex; align-items: center; gap: 8px;">
            <h1>FraudFlow Intelligence</h1>
            <span class="official-node-tag">MHA / I4C NODE</span>
          </div>
          <div class="brand-subtitle">
            <span>National Cyber Crime Reporting Portal (NCRP) &bull; Inter-Bank Decision Support System</span>
          </div>
        </div>
      </div>
    </div>'''
    html = html[:old_brand_title.start()] + new_brand_title + html[old_brand_title.end():]
    print('Brand titles updated to official MHA/I4C style')

# 2. Update Wave Card inside finnova-card-hero with authentic forensic gridlines & axes
old_svg = re.search(r'<svg class="dash-sparkwave-svg"[^>]*>.*?</svg>', html, re.DOTALL)
if old_svg:
    new_svg = '''<svg class="dash-sparkwave-svg" id="dash-sparkwave-svg" viewBox="0 0 600 125" preserveAspectRatio="none">
              <defs>
                <linearGradient id="finnovaWaveGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stop-color="rgba(2, 132, 199, 0.40)" />
                  <stop offset="60%" stop-color="rgba(2, 132, 199, 0.10)" />
                  <stop offset="100%" stop-color="rgba(15, 23, 42, 0)" />
                </linearGradient>

                <linearGradient id="finnovaLineGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stop-color="#38bdf8" />
                  <stop offset="60%" stop-color="#0284c7" />
                  <stop offset="100%" stop-color="#0ea5e9" />
                </linearGradient>
              </defs>

              <!-- Forensic Telemetry Gridlines -->
              <line x1="0" y1="28" x2="600" y2="28" stroke="rgba(148, 163, 184, 0.12)" stroke-dasharray="3,3" />
              <line x1="0" y1="65" x2="600" y2="65" stroke="rgba(148, 163, 184, 0.12)" stroke-dasharray="3,3" />
              <line x1="0" y1="105" x2="600" y2="105" stroke="rgba(148, 163, 184, 0.20)" />

              <!-- Forensic Y-Axis Velocity Calibration Ticks -->
              <text x="6" y="24" fill="#64748b" font-size="8" font-family="'JetBrains Mono', monospace">₹3.5L/m [CRITICAL]</text>
              <text x="6" y="61" fill="#64748b" font-size="8" font-family="'JetBrains Mono', monospace">₹1.5L/m [LAYER-1]</text>
              <text x="6" y="101" fill="#475569" font-size="8" font-family="'JetBrains Mono', monospace">₹0</text>

              <!-- Dynamic Area & Line Paths -->
              <path id="dash-sparkwave-path-area" d="M 0 95 Q 80 90, 150 80 T 300 70 T 420 50 T 510 30 L 510 120 L 0 120 Z" fill="url(#finnovaWaveGrad)" />
              <path id="dash-sparkwave-path-line" d="M 0 95 Q 80 90, 150 80 T 300 70 T 420 50 T 510 30 L 600 28" fill="none" stroke="url(#finnovaLineGrad)" stroke-width="2.4" />

              <!-- Terminal Marker & Pulse -->
              <line id="dash-sparkwave-marker-line" x1="510" y1="30" x2="510" y2="105" stroke="#38bdf8" stroke-width="1.8" stroke-dasharray="3,3" opacity="0.9" />
              <circle id="dash-sparkwave-pulse-ring" cx="510" cy="30" r="4.5" fill="none" stroke="#38bdf8" stroke-width="2" class="dash-sparkwave-pulse-ring">
                <animate attributeName="r" values="4.5;22;4.5" dur="1.8s" repeatCount="indefinite" />
                <animate attributeName="opacity" values="1;0.05;1" dur="1.8s" repeatCount="indefinite" />
                <animate attributeName="stroke-width" values="2.2;0.5;2.2" dur="1.8s" repeatCount="indefinite" />
              </circle>
              <circle id="dash-sparkwave-marker-dot" cx="510" cy="30" r="4.5" fill="#ffffff" stroke="#0284c7" stroke-width="2.5">
                <animate attributeName="r" values="4;5.5;4" dur="1.2s" repeatCount="indefinite" />
              </circle>

              <!-- X-Axis Temporal Timeline Calibration -->
              <text x="50" y="119" fill="#64748b" font-size="7.5" font-family="'JetBrains Mono', monospace">T0 10:42 INFLOW</text>
              <text x="250" y="119" fill="#64748b" font-size="7.5" font-family="'JetBrains Mono', monospace">HOP 2 10:56 TRANSIT</text>
              <text x="470" y="119" fill="#38bdf8" font-weight="700" font-size="7.5" font-family="'JetBrains Mono', monospace">T_CASHOUT 11:15</text>
            </svg>'''
    html = html[:old_svg.start()] + new_svg + html[old_svg.end():]
    print('Wave SVG enhanced with forensic telemetry axes!')

# 3. Update Card Tag
html = html.replace(
    '<span class="finnova-card-tag">Forensic Risk Score</span>',
    '<span class="finnova-card-tag">Forensic Risk &amp; Dispersion Velocity</span>'
)

# 4. Bump Cache Version
html = html.replace('styles.css?v=2.1.2', 'styles.css?v=2.2.0')
html = html.replace('app.js?v=2.1.2', 'app.js?v=2.2.0')

with open('app/static/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('index.html tactical enhancements applied successfully!')
